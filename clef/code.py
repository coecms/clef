#!/usr/bin/env python
# Copyright 2018 ARC Centre of Excellence for Climate Extremes
# author: Paola Petrelli <paola.petrelli@utas.edu.au>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import os
import pandas as pd
import json
import re
import pkg_resources
import itertools

from sqlalchemy import any_

from .db import connect, Session
from .model import Path, C5Dataset, C6Dataset, ExtendedMetadata, CordexDataset
from .exception import ClefException
from .esgf import esgf_query
from .helpers import convert_periods, time_axis, check_values, check_keys, fix_model, fix_path, \
                     get_facets, get_range, get_version, get_keys, load_vocabularies, get_member


def search(session, project='CMIP5', latest=True, **kwargs):
    """Call local query interactively.

    Can be used when in python script, first checks that the arguments names
       and values are correct, changes model name where necessary. Then calls local_query
       to run the query on DB.

    Args:
        session (SQLAlchemy obj): the db session
        project (str): data project (default CMIP5)
        latest (bool): version latest (default True) or all (False)
        kwargs (dict): query constraints

    Returns:
        results (pandas.DataFrame): each row describes one simulation matching the constraints

    """

    # make sure project is upper case 
    project=project.upper()
    # load dictionary of valid keys for project facets
    valid_keys = get_keys(project)
    # check all passed keys are valid
    args = check_keys(valid_keys, kwargs)
    # load dictionary of valid keys for project facets
    vocabularies = load_vocabularies(project)
    check_values(args, project, vocabularies)
    if 'model' in args.keys():
        args['model'] = fix_model(project, [args['model']])[0]
    results = local_query(session, project, latest, **args)
    if latest:
        results = local_latest(results)
    return results


def matching(session, cols, fixed, project='CMIP5', local=True, latest=True, **kwargs):
    """Call and_filter after executing local or remote query of passed constraints
      
    This function is called by the command line with the 'and' argument.
    Can also be imported and used to performed a query and apply a filter interactively. 

    Args:
        session (SQLAlchemy session obj): database session
        cols (list): attributes for which all values should be present
        fixed (list): attributes used to define a simulation (i.e. model/ensemble/version)
        project (string): project, i.e. CMIP5 (default)/CMIP6
        local (boolean): default local query (True) or remote query (False)
        latest (boolean): default True returns only latest version
        kwargs (dictionary): query constraints

    Returns:
        output of and_filter (pandas.dataFrame): query results and  filter results

    """

    res_list = [] 
    try:
        # use local search
        if local:
            msg = "There are no simulations stored locally"
            # perform the query for each variable separately and concatenate the results
            combs = [dict(zip(kwargs, x)) for x in itertools.product(*kwargs.values())]
            for c in combs:
                res_list.append(search(session,project=project.upper(),
                                            latest=latest, **c))
            results = pd.concat(res_list, ignore_index=True)
        # use ESGF search
        else:
            msg = "There are no simulations currently available on the ESGF nodes"
            kwquery = {k:tuple(v) for k,v in kwargs.items()}
            kwquery['project']=project.upper()
            attrs = ['dataset_id', 'version'] # datetime_start, datetime_stop
            attrs.extend( load_vocabularies(project)['attributes'])
            query=None
            response = esgf_query(query, ','.join(attrs), latest=latest, **kwquery)
            # can't create dataframe in one go because many values are unidimensional lists
            res_list = []
            for row in response['response']['docs']:
                row['version'] = row['dataset_id'].split("|")[0].split(".")[-1],
                res_list.append({k:(v[0] if isinstance(v,list) else v) for k,v in row.items()})
            results = pd.DataFrame(res_list)

    except Exception as e:
        print('ERROR',str(e))
        return None, None

    # if nothing turned by query print warning and return
    if len(results.index) == 0:
        print(f'{msg} for {kwargs}')
        final = None
        selection = None
    else:
        final, selection  = and_filter(results, cols, fixed, **kwargs)
    return final, selection


def call_local_query(s, project, latest, **kwargs):
    """Call local_query for each combination of constraints passed as argument

    Args:
        s (SQLAlchemy session obj): database session
        project (string): project, i.e. CMIP5/CMIP6
        latest (boolean): True returns only latest version
        kwargs (dictionary): query constraints

    Returns:
        datasets (pandas.DataFrame): the full query results
        paths (list): directory/file paths depending on format chosen

    """

    ds_list = [] 
    paths = []
    combs = [dict(zip(kwargs, x)) for x in itertools.product(*kwargs.values())]
    for c in combs:
         ds_list.append(local_query(s,project=project, latest=latest, **c))
    datasets = pd.concat(ds_list, ignore_index=True)
    
    paths = datasets['path'].tolist()
    return datasets, paths


def local_query(session, project='CMIP5', latest=True, **kwargs):
    """Query DB matching directly the constraints to the file attributes instead of querying first the ESGF

    Args:
        session (SQLAlchemy session obj): database session
        project (string): project, i.e. CMIP5 (default)/CMIP6
        latest (boolean): True (default) returns only latest version
        kwargs (dictionary): query constraints

    Returns:
      results (pandas.DataFrame): each row describe one simulation matching the constraints

    """ 

    # make sure project is upper case 
    project = project.upper()
    r = build_query(session, project, **kwargs)

    # run the sql using pandas read_sql,index data using path, returns a dataframe
    df = pd.read_sql(r.selectable, con=session.connection())
    df = df.rename(columns={'path': 'opath'})

    # fix path by substituing output1/2 with combined, separate path from filenames
    fix_paths = df['opath'].apply(fix_path, latest=latest)
    df['path'] = fix_paths.map(os.path.dirname)
    # added to eliminate wrong paths for mk3.6.0 once that is fixed might be removed
    df = df[df.path != '/path/todelete']
    df['filename'] = df['opath'].map(os.path.basename)

    # group by path
    mcols = ['filename','period']
    agg_dict = {k: ('first' if k not in mcols else set) for k in list(df)}
    res = df.groupby(['path']).agg(agg_dict)

    # apply postprocessing function to each row
    res = res.apply(post_local, axis=1)
    # remove unuseful columns
    todel = ['opath','r','i','p','f','period']
    cols = [c for c in todel if c in res.columns]
    res = res.drop(columns=cols)
    return res


def build_query(session, project, **kwargs):
    """Build local query syntax.

    Args:
        session (SQLAlchemy obj): the db session
        project (str): data project
        kwargs (dict): query constraints

    Returns:
        r: (str) SQL query syntax to execute 

    """   

    # for cmip5, cordex separate var from other constraints 
    if project in ['CMIP5', 'CORDEX'] and 'variable' in kwargs:
        var = kwargs.pop('variable')
    if project in ['CMIP5', 'CORDEX'] and 'experiment_family' in kwargs.keys():
        family = kwargs.pop('experiment_family')
    if project == 'CMIP6' and 'activity_id' in kwargs.keys():
        activity = kwargs.pop('activity_id')
    ctables={'CMIP5': [C5Dataset, Path.c5dataset],
          'CMIP6': [C6Dataset, Path.c6dataset],
          'CORDEX': [CordexDataset, Path.cordexdataset] }
    family_dict = {'RCP': ['%rcp%'],
                   'ESM': ['esm%'],
                   'Atmos-only': ['sst%', 'amip%', 'aqua%'],
                   'Control': ['sstClim%', '%Control'],
                   'decadal': ['decadal%','noVolc%', 'volcIn%'],
                   'Idealized': ['%CO2'],
                   'All': ['%'],
                   'Paleo': ['lgm','midHolocene', 'past1000'],
                   'Historical': ['historical%','%Historical']}

    r = (session.query(Path.path.label('path'),
         *[c.label(c.name) for c in ctables[project][0].__table__.columns if c.name != 'dataset_id'],
         *[c.label(c.name) for c in ExtendedMetadata.__table__.columns if c.name != 'file_id']
        )
        .join(Path.extended)
        .join(ctables[project][1])
        .filter_by(**kwargs))
    if 'family' in locals() and project == 'CMIP5':
          r =r.filter(C5Dataset.experiment.like(any_(family_dict[family])))
    if 'family' in locals() and project == 'CORDEX':
          r =r.filter(CordexDataset.experiment.like(any_(family_dict[family])))
    if 'var' in locals(): 
        r = r.filter(ExtendedMetadata.variable == var)
    if 'activity' in locals():
          r =r.filter(C6Dataset.activity_id.like("%"+activity+"%"))
    return r


def post_local(row):
    """Postprocess local query results row by row 
    """ 
    row['periods'] = convert_periods(row['period'])
    row['fdate'], row['tdate'] = get_range(row['periods'])
    row['time_complete'] = time_axis(row['periods'],row['fdate'],row['tdate'])
    # make sure a version is available even for CMIP6 where is usually None
    if row['version'] is None:
        row['version'] = get_version(row['path'])
    # check if 'f' in row keys to exclude CMIP5 queries
    if 'f' in row.keys() and any(x in row['member_id'] for x in ['r0','i0','p0','f0']):
        row['member_id'] = get_member(row['path'])
        # variant_labele could actually be different if sub-experiment present but for the moment this should be ok
        row['variant_label'] = row['member_id']
    return row


def and_filter(df, cols, fixed, **kwargs):
    """AND filter query results

    Find simulations that have all the values passed for each attribute listed by cols.
    A simulation is defined by the attributes passed in the list fixed.

    Args:
        df (pandas.DataFrame): query results to filter
        cols (list): attributes for which we want all values to be present
        fixed (list): attributes used to define a simulation (i.e. model/ensemble/version)
        kwargs (dictionary): query constraints

    Returns:
        rows (pandas.DataFrame): subset of original results that satisfy filter
        selection (pandas.DataFrame): filtered rows grouped by possible combination

    """

    # create a new column with pairs of values for the 'cols' attributes
    if len(cols) >= 1:
        comb_val = list(zip(*[df[c] for c in cols]))
        df2 = df.assign(comb=comb_val)
    # list all possible combinations of values for 'cols' attributes
        comb = list(itertools.product(*[kwargs[c] for c in cols]))
    else:
        raise ClefException('List of attributes to apply filter to is empty')

    # reset index so index is available as column
    df2 = df2.reset_index()
    # useful is a list of fields to retain in the table
    useful =  set(['version', 'source_id', 'model', 'path','dataset_id', 'domain',
        'cmor_table','table_id', 'ensemble', 'member_id', 'driving_experiment',
        'model_id', 'frequency', 'driving_model', 'rcm_version']) - set(fixed)
    fields = ['comb'] + [f for f in useful if f in [c for c in df.columns.values]]
    # define the aggregation dictionary
    agg_dict = {k: set for k in fields}
    agg_dict['index'] = lambda x: tuple(x)
    # group table data by the columns listed in 'fixed' i.e. model and ensemble
    # and aggregate rows with matching values creating a set for each including path and version
    d = (df2.groupby(fixed)
       .agg(agg_dict))
    # create a filter to select the rows where the lenght of the simulation combinations 
    # is equal to the number of "cols" combinations and apply to table
    selection = d[d['comb'].map(len) == len(comb)]
    # select full rows from original dataframe using original index 
    if len(selection.index) > 0 :
        fullrow = df2[df2.index.isin(selection['index'].sum())]
    else:
        fullrow = pd.DataFrame(columns=df2.columns)
    return fullrow, selection


def write_csv(df):
    """Write query results to csv file
    """
    if len(df.index) == 0:
        print(f'Nothing to write to csv file')
        return
    if 'cordex_domain' in df.columns:
        project = 'CORDEX'
    elif 'experiment_id' in df.columns:
        project = 'CMIP6'
    else:
        project = 'CMIP5'
    csv_file = f"{project}_query.csv"
    ignore = ['periods', 'filename', 'institute', 'project', 'institution_id','realm', 'product']
    columns = [x for x in df.columns if x not in ignore]
    try:
        with open(csv_file, 'w') as csvfile:
            csvfile.write(df[columns].to_csv())
        print(f'Saving to {csv_file}')
    except IOError:
        print("I/O error")


def stats(results, project):
    """Return some stats on query results

    Args:
        results (pandas.DataFrame): each row describes one simulation matching the constraints
        project (string): the dataset project (CMIP5, CMIP6, CORDEX)
    
    Returns:
        member_by_model (pandas.DataFrame): results rearranged as model: members list, members number

    """

    attrs = get_facets(project)
    # group results by model and create members list, finally count memebrs number for each model
    member_by_model = results.groupby(attrs['m'])[attrs['en']] \
                        .agg(members='unique', count='nunique')
    return member_by_model 


def print_stats(results, project):
    """Call stats function and then print out query statistics

    Args:
        results (pandas.DataFrame): each row describes one simulation matching the constraints
        project (string): the dataset project (CMIP5, CMIP6, CORDEX)

    """
    if len(results.index) == 0:
        print('No results are available for this query')
        return
    sdf = stats(results, project)

    print("\nQuery summary")
    # print total number of models and their names
    print(f"\n{sdf.index.nunique()} model/s are available:")
    for m in sorted(sdf.index):
        print(m, end=" ")
    print()
    print(f"\nA total of {sdf['count'].sum()} unique model-member combinations are available.")
    
    # print models and their members, grouped by number of members
    for key, item in sdf.groupby('count'):
        print(f"\n  {len(item.index)} model/s have {key} member/s:\n")
        for m in item.index.values:
            print(f"     {m}: {', '.join(item.loc[m,'members'])}")
    print("\n")


def local_latest(results):
    """Sift through local query results dataframe and return only the latest versions

    Args:
        results (pandas.DataFrame): each row describes one simulation matching the constraints
    Returns:
        results (pandas.DataFrame): same but only latest versions
    """

    if len(results.index) <= 1:
        return results
    # separate all the attributes which could be different between two versions
    separate = ['path', 'version', 'time_complete', 'filename','fdate', 'tdate', 'periods']
    cols = [k for k in results.columns if k not in separate]
    results = results.sort_values('version').drop_duplicates(subset=cols, keep='last')
    return results


def ids_df(dids):
    """Convert dataset_ids in DataFrame in same style as query results

    Args:
      dids (list): list of dataset_ids

    Returns:
        results (pandas.DataFrame): each row describes one simulation matching the constraints

    """
    project = dids[0].split(".")[0]
    facets = get_facets(project.upper())
    if project == 'CMIP6':
        facets_list = ['project', 'activity_id', 'institution_id', 'source_id',
                  'experiment_id', 'member_id', 'table_id', 'variable_id',
                  'grid_label', 'version']
    elif project == 'cmip5':
        facets_list = ['project', 'product', 'institute', 'model', 'experiment',
                       'time_frequency', 'realm', 'cmor_table', 'ensemble', 'version']
    elif project == 'cordex':
        facets_list = ['project', 'product', 'domain', 'institute', 'driving_model',
             'driving_experiment', 'ensemble', 'model_id', 'rcm_version', 'frequency',
             'variable', 'version']
    else:
        print(f'Warning: project {project} not available')
        return results 
    res_list = []
    for i, did in enumerate(dids):
        df = pd.DataFrame([{k:v for k,v in zip(facets_list,did.split("."))}], index=[i], columns=facets_list)
        res_list.append(df)
    results = pd.concat(res_list, ignore_index=True)
    return results


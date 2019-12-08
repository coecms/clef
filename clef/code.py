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
import csv
import json
import re
import pkg_resources
import itertools

from sqlalchemy import any_

from .db import connect, Session
from .model import Path, C5Dataset, C6Dataset, ExtendedMetadata
from .exception import ClefException
from .esgf import esgf_query
from .helpers import convert_periods, time_axis, check_values, check_keys, fix_model, fix_path, \
                     get_facets, get_range, get_version, get_keys, load_vocabularies


def search(session, project='CMIP5', latest=True, **kwargs):
    """Call local query interactively.

    Can be used when in python script, first checks that the arguments names
       and values are correct, changes model name where necessary. Then calls local_query
       to run the query on MAS.

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


def build_query(session, project, **kwargs):
    """Build local query syntax.

    Args:
        session (SQLAlchemy obj): the db session
        project (str): data project
        kwargs (dict): query constraints

    Returns:
        r: (str) SQL query syntax to execute 

    """   

    # for cmip5 separate var from other constraints
    if project == 'CMIP5' and 'variable' in kwargs.keys():
        var = kwargs.pop('variable')
    if project == 'CMIP5' and 'experiment_family' in kwargs.keys():
        family = kwargs.pop('experiment_family')
    ctables={'CMIP5': [C5Dataset, Path.c5dataset],
          'CMIP6': [C6Dataset, Path.c6dataset]}
    family_dict = {'RCP': ['%rcp%'],
                   'ESM': ['esm%'],
                   'Atmos-only': ['sst%', 'amip%', 'aqua%'],
                   'Control': ['sstClim%', '%Control'],
                   'decadal': ['decadal%','noVolc%', 'volcIn%'],
                   'Idealized': ['%CO2'],
                   'Paleo': ['lgm','midHolocene', 'past1000'],
                   'historical': ['historical%','%Historical']}
    r = (session.query(Path.path.label('path'),
         *[c.label(c.name) for c in ctables[project][0].__table__.columns if c.name != 'dataset_id'],
         *[c.label(c.name) for c in ExtendedMetadata.__table__.columns if c.name != 'file_id']
        )
        .join(Path.extended)
        .join(ctables[project][1])
        .filter_by(**kwargs))
    if 'family' in locals():
          r =r.filter(C5Dataset.experiment.like(any_(family_dict[family])))
    if 'var' in locals(): 
        r = r.filter(ExtendedMetadata.variable == var)
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
    return row


def local_query(session, project='CMIP5', latest=True, **kwargs):
    """Query MAS matching directly the constraints to the file attributes instead of querying first the ESGF

    Args:

      session the db session
      project 'CMIP5' by default
      latest True by default
      kwargs a dictionary with the query constraints
    Returns:
      results (pandas.DataFrame): each row describe one simulation matching the constraints

    """ 

    # make sure project is upper case 
    project = project.upper()
    r = build_query(session, project, **kwargs)


    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', -1)
    # run the sql using pandas read_sql,index data using path, returns a dataframe
    df = pd.read_sql(r.selectable, con=session.connection())
    df = df.rename(columns={'path': 'opath'})
    # temporary(?) fix to substitute output1/2 with combined
    fix_paths = df['opath'].apply(fix_path, latest=latest)
    df['path'] = fix_paths.map(os.path.dirname)
    df['filename'] = df['opath'].map(os.path.basename)
    mcols = ['filename','period']
    agg_dict = {k: ('first' if k not in mcols else list) for k in list(df)}
    res = df.groupby(['path']).agg(agg_dict)
    res.apply(post_local, axis=1)

    #res['periods'] = res.period.apply(convert_periods)
    #res['fdate'], res['tdate'] = zip(*res['periods'].map(get_range))
    #res['time_complete'] = res.apply(lambda x: time_axis(x['periods'],x['fdate'],x['tdate']), axis=1)
    # make sure a version is available even for CMIP6 where is usually None
    #mask = res['version'].isnull()
    #res.loc[mask, 'version'] = res.loc[mask, 'path'].apply(get_version)
    # remove unuseful columns
    todel = ['opath','r','i','p','f','period']
    cols = [c for c in todel if c in res.columns]
    res = res.drop(columns=cols)
    return res


def call_local_query(s, project, oformat, latest, **kwargs):
    """Call local_query for each combination of constraints passed as argument, return datasets/files paths
    """

    datasets = pd.DataFrame() 
    paths = []
    combs = [dict(zip(kwargs, x)) for x in itertools.product(*kwargs.values())]
    for c in combs:
         datasets = datasets.append(local_query(s,project=project, latest=latest, **c), ignore_index=True)
    if oformat == 'dataset':
        for d in datasets:
            paths.append(d['path'])
    elif oformat == 'file':
        for d in datasets:
            paths.extend([d['path']+"/" + x for x in d['filename']])
    return datasets, paths


def and_filter(tab, cols, fixed, **kwargs):
    """Filter query results to find all the simulations that have
        all the different values passed for the attributes listed in cols.
        A simulation is defined by the attributes passed in the list fixed.
          tab (dataframe) the results of the query
          cols (list) the attributes for which we want all values to be present
          fixed (list) are the attributes used to define a simulation (i.e. model/ensemble/version)
          kwargs (dictionary) are the query constraints
        Returns:
 query results and a list of dictionaries each representing a 'simulation'
                 that has all the requested values for "cols"
    """
    # if you want to select all the values for two or more columns
    # create a new column with their values paired to use for the aggregation
    if len(cols) >= 1:
        tab['comb'] = list(zip(*[tab[c] for c in cols]))
    # list all combinations of cols attributes
        comb = list(itertools.product(*[kwargs[c] for c in cols]))
    # define the aggregation dictionary first
    # useful is a list of fields to retain in the table, the values
    # get added to final fields list only if in results.keys
    useful =  set(['version', 'source_id', 'model', 'path','dataset_id',
              'cmor_table','table_id', 'ensemble', 'member_id']) - set(fixed)
    fields = ['comb'] + [f for f in useful if f in [c for c in tab.columns.values]]
    agg_dict = {k: set for k in fields}
    # group table data by the columns listed in fix_col i.e. model and ensemble
    # and aggregate rows with matching values creating a set for each including path and version
    # reset the table indexes
    d = (tab.groupby(fixed)
       .agg(agg_dict))
       #.reset_index())
    # create a filter to select the rows where the lenght of the simulation combinations is
    # is equal to the number of "cols" combinations and apply to table
    selection = d[d['comb'].map(len) == len(comb)]
    # to subset results based on selection, create a list of tuple with the fixed attributes for selection (sel_fixed)
    # then do the same for each results and append them to a new list only if they are in sel_fixed
    print("I am here before sel")
    fullrow = tab[tab.index.isin(selection.index)]
    print("I am here after sel")
    #sel_attrs = []
    #sel_fixed = []
    #selection['fixed'] = "-".join(selection[a] for a in fixed
    #for sim in selection:
    #    sel_fixed.append(tuple([sim[a] for a in fixed]))
    #for sim in results:
    #    if (tuple([sim[a] for a in fixed])) in sel_fixed:
    #        sel_attrs.append(sim)
    return fullrow, selection


def matching(session, cols, fixed, project='CMIP5', local=True, latest=True, **kwargs):
    """Call and_filter after executing local or remote query of passed constraints
        :session: database session
        :project: ESGF project to search (CMIP5/CMIP6)
          cols (list) the attributes for which we want all values to be present
          fixed (list) are the attributes used to define a simulation (i.e. model/ensemble/version)
          project (string) the project, i.e. CMIP5 (default)/CMIP6
          local (boolean) if local query (default) or remote query (False)
          latest (boolean) if True (default) returns only latest version
          kwargs (dictionary) are the query constraints
        Returns:
 output of and_filter: query results and a filter selection lists
    """

    results = pd.DataFrame() 
    try:
        # use local search
        if local:
            msg = "There are no simulations stored locally"
            # perform the query for each variable separately and concatenate the results
            combs = [dict(zip(kwargs, x)) for x in itertools.product(*kwargs.values())]
            for c in combs:
                results = results.append(search(session,project=project.upper(),latest=latest, **c),
                               ignore_index=True)
        # use ESGF search
        else:
            msg = "There are no simulations currently available on the ESGF nodes"
            kwquery = {k:tuple(v) for k,v in kwargs.items()}
            kwquery['project']=project.upper()
            if project == 'CMIP5':
                fields = 'dataset_id,model,experiment,variable,ensemble,cmor_table,version'
            else:
                fields = ",".join(['dataset_id','source_id','experiment_id','variable_id',
                                   'activity_id','table_id','version','grid_label','source_type',
                                   'frequency','member_id','sub_experiment_id'])
            query=None
            response = esgf_query(query, fields, latest=latest, **kwquery)
            for row in response['response']['docs']:
                version = row['dataset_id'].split("|")[0].split(".")[-1]
                results.append({k:(v[0] if isinstance(v,list) else v) for k,v in row.items()})
                results[-1]['version'] = version

    except Exception as e:
        print('ERROR',str(e))
        return None

    # if nothing turned by query print warning and return
    if len(results.index) == 0:
        print(f'{msg} for {kwargs}')
        return None, None
    return and_filter(results, cols, fixed, **kwargs)

def write_csv(list_dicts):
    """Write query results to csv file
    """
    if len(list_dicts) == 0:
        print(f'Nothing to write to csv file')
        return
    project = list_dicts[0].get("project", "result")
    csv_file = f'{project.upper()}_query.csv'
    ignore = ['periods', 'filename', 'institute', 'project', 'institution_id','realm', 'product']
    columns = [x for x in list_dicts[0].keys() if x not in ignore]
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, extrasaction='ignore', fieldnames=columns)
            writer.writeheader()
            writer.writerows(list_dicts)
    except IOError:
        print("I/O error")

def stats(results):
    """ Return some stats on search results
      results a list of dictonaries containing results
    Returns:
 stats_dict a dictionary containing the stats to print
    """
    stats_dict = {}
    attrs = get_facets(results[0]['project'].upper())
    # get number of unique models
    stats_dict['models'] = set(x[attrs['m']] for x in results)
    # get number of unique models/ensembles
    stats_dict['model_member'] = set((x[attrs['m']], x[attrs['en']]) for x in results)
    # get number of unique ensembles for each model
    stats_dict['members'] = {m:[] for m in stats_dict['models']}
    for m,en in stats_dict['model_member']:
        stats_dict['members'][m].append(en)
    return stats_dict


def print_stats(results):
    """ call stats function and then print out query statistics """
    if len(results) == 0:
        print('No results are available for this query')
        return
    stats_dict = stats(results)
    print('\nQuery summary')
    print(f'\n{len(stats_dict["models"])} model/s are available:')
    for m in sorted(stats_dict["models"]):
        print(m, end=' ')
    print()
    print(f'\nA total of {len(stats_dict["model_member"])} unique model-member combinations are available.')
    member_num = {k: len(v) for k,v in stats_dict['members'].items()}
    member_num = {len(v): [] for v in stats_dict['members'].values()}
    for k,v in stats_dict['members'].items():
        member_num[len(v)].append(k)
    for num in sorted(member_num.keys()):
        print(f'\n{len(member_num[num])} model/s have {num} member/s:')
        for m in sorted(member_num[num]):
            print(m, end=' ')
        print()


def local_latest(results):
    """Sift through local query results dataframe and return only the latest versions
    """
    if len(results.index) <= 1:
        return results
    # separate all the attributes which could be different between two versions
    separate = ['path', 'version', 'time_complete', 'filename','fdate', 'tdate', 'periods']
    cols = [k for k in results.columns if k not in separate]
    results = results.sort_values('version').drop_duplicates(subset=cols, keep='last')#.sort_index()
    return results


def ids_dict(dids):
    """Gets a list of dataset_ids and return a list of dictionaries in same style as local query results

    Args:

      dids (list): list of dataset_ids

    Returns:
        results (list): list of dictionary, one for id listing simulation attributes

    """
    results = []
    project = dids[0].split(".")[0]
    if project == 'CMIP6':
        facets_list = ['project', 'activity_id', 'institution_id', 'source_id',
                  'experiment_id', 'member_id', 'table_id', 'variable_id',
                  'grid_label', 'version']
    elif project == 'cmip5':
        facets_list = ['project', 'product', 'institute', 'model', 'experiment',
                       'time_frequency', 'realm', 'cmor_table', 'ensemble', 'version']
    else:
        print(f'Warning: project {project} not available')
        return results 
    for did in dids:
        results.append({k:v for k,v in zip(facets_list,did.split("."))})
    return results


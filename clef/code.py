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
from .db import connect, Session
from .model import Path, C5Dataset, C6Dataset, ExtendedMetadata
from .exception import ClefException
from .esgf import esgf_query
from datetime import datetime, timedelta
from sqlalchemy import any_, or_
from sqlalchemy.orm import aliased
from itertools import groupby
import pandas
import logging
import sys
import os
import json
import pkg_resources
import itertools
from calendar import monthrange
import re

 
def search(session, project='cmip5', **kwargs):
    """
    This call the local query when integrated in python script before running query checks
    that the arguments names and values are correct and change model name where necessary
    """
    valid_keys = get_keys(project)
    args = check_keys(valid_keys, kwargs)
    vocabularies = load_vocabularies(project)
    check_values(vocabularies, project, args)
    if 'model' in args.keys():
        fix_model(project, args['model'])
    return local_query(session, project, **args)


def local_query(session, project='cmip5', **kwargs):
    """
    """
    # create empty list for results dictionaries
    # each dict will represent a file matching the constraints
    results=[]
    project = project.lower()
    # for cmip5 separate var from other constraints 
    if project == 'cmip5' and 'variable' in kwargs.keys():
        var = kwargs.pop('variable')
    ctables={'cmip5': [C5Dataset, Path.c5dataset],
          'cmip6': [C6Dataset, Path.c6dataset] }
        
    if 'var' in locals():
        r = (session.query(Path.path.label('path'),
            *[c.label(c.name) for c in ctables[project][0].__table__.columns if c.name != 'dataset_id'],
            *[c.label(c.name) for c in ExtendedMetadata.__table__.columns if c.name != 'file_id']
           )
           .join(Path.extended)
           .join(ctables[project][1])
           .filter_by(**kwargs)
           .filter(ExtendedMetadata.variable == var))
    else:
        r = (session.query(Path.path.label('path'),
            *[c.label(c.name) for c in ctables[project][0].__table__.columns if c.name != 'dataset_id'],
            *[c.label(c.name) for c in ExtendedMetadata.__table__.columns if c.name != 'file_id']
           )
           .join(Path.extended)
           .join(ctables[project][1])
           .filter_by(**kwargs))

    # run the sql using pandas read_sql,index data using path, returns a dataframe
    df = pandas.read_sql(r.selectable, con=session.connection())
    # temporary(?) fix to substitute output1/2 with combined
    fix_paths = df['path'].map(fix_path)
    df['pdir'] = fix_paths.map(os.path.dirname)
    df['filename'] = df['path'].map(os.path.basename)
    res = df.groupby(['pdir'])
    results=[]
    cols = [x for x in list(df) if x not in ['filename','path','period'] ]
    for g,v in res.groups.items():
        gdict={}
        gdict['filenames'] = df['filename'].iloc[list(v)].tolist()
        nranges = df['period'].iloc[list(v)].tolist()
        for c in cols:
            gdict[c] = df[c].iloc[list(v)].unique()[0]
        gdict['periods'] = convert_periods(nranges, gdict['frequency'])
        gdict['fdate'], gdict['tdate'] = get_range(gdict['periods'])
        gdict['time_complete'] = time_axis(gdict['periods'],gdict['fdate'],gdict['tdate'])
        results.append(gdict)
    return results

def get_range(periods):
    """
    Convert a list of NumericRange period to a from-date,to-date separate values
    input: periods list of tuples representing lower and upper end of temporal interval, values are strings 
    return: from_date, to_date as strings
    """
    try:
        lower, higher = int(periods[0][0]), int(periods[0][1])
        for nr in periods[1:]:
            low, high = int(nr[0]), int(nr[1])
            lower = min(low,lower)
            higher = max(high, higher)
        # to keep into account the open interval
        higher = higher
    except:
        return None, None
    return str(lower), str(higher)

def convert_periods(nranges,frequency):
    """
    Convert period Numeric ranges to dates intervals and build the time axis
    input: nranges a list of each file period
    input: frequency timestep frequency 
    return: periods list of tuples representing lower and upper end of temporal interval, values are strings 
    """
    freq = {'mon': 'M', 'day': 'D', '6hr': '6H'}
    periods = []
    if len(nranges) == 0:
        return periods
    for r in nranges:
        if r is None:
            continue 
        lower, upper = str(r.lower), str(r.upper - 1)
        if len(lower) == 6:
            lower += '01'
            upper += str(monthrange(int(upper[0:4]),int(upper[4:6]))[1])
        periods.append((lower,upper))
    return periods

def time_axis(periods,fdate,tdate):
    """
    Check that files constitute a contiguos time axis
    input: periods a list of ('from_date', 'to_date') for each file
    input: fdate, tdate from_date and to_date strings
    return: True or False
    """
    if periods == []:
        return None 
    sp = sorted(periods)
    nextday = fdate
    i = 0
    contiguos = True 
    try:
        while sp[i][0] == nextday:
            t = datetime.strptime(sp[i][1],'%Y%m%d') + timedelta(days=1)
            nextday = t.strftime('%Y%m%d')
            i+=1
            if i >= len(sp):
                break
        else:
            contiguos = False 
    except:
        return None 
    return contiguos

def get_keys(project):
    """
    Define valid arguments keys based on project
    """
    # valid_keys has as keys tuple of all valid arguments and as values dictionaries 
    # representing the corresponding facet for CMIP5 and CMIP6
    # ex. ('variable', 'variable_id', 'v'): {'cmip5': 'variable', 'cmip6': 'variable_id'}
    fkeys = pkg_resources.resource_filename(__name__, 'data/valid_keys.json')
    with open(fkeys, 'r') as f:
         data = json.loads(f.read()) 
    valid_keys = {v[project]: k.split(":") for k,v in data.items() if v[project] != 'NA'}
    return valid_keys

def check_keys(valid_keys, kwargs):
    """
    Check that arguments keys passed to search are valid, if not print warning and exit
    """
    # load dictionary to check arguments keys are valid
    # rewrite kwargs with the right facet name
    args = {}
    for key,value in kwargs.items():
        facet = [k for k,v in valid_keys.items() if key in v]
        if facet==[]:
            print(f"Warning {key} is not a valid constraint name")
            print(f"Valid constraints are:\n{valid_keys.values()}")
            if "JPY_PARENT_PID" in os.environ:
                exit()
            else:
                sys.exit()
        else:
            args[facet[0]] = value
    return args

def check_values(vocabularies, project, args):
    """
    Check that arguments values passed to search are valid, if not print warning and exit
    """
    # load dictionaries to check arguments values are valid
    if project == 'cmip5':
        model, realm, variable, frequency, table, experiment, experiment_family = vocabularies
    elif project == 'cmip6':
        source_id, realm, variable_id, frequency, table_id, experiment_id, activity_id, source_type = vocabularies
    else:
        print(f'Search for {project} not yet implemented')
        if "JPY_PARENT_PID" in os.environ:
            exit()
        else:
            sys.exit()
    for k,v in args.items():
        if k in locals() and v not in locals()[k]:
            print(f'{v} is not a valid value for {k}')
            if "JPY_PARENT_PID" in os.environ:
                exit()
            else:
                sys.exit()
    return args

def load_vocabularies(project):
    ''' '''
    project = project.upper()
    vfile = pkg_resources.resource_filename(__name__, 'data/'+project+'_validation.json')
    mfile = pkg_resources.resource_filename(__name__, 'data/'+project+'_validation.json')
    with open(vfile, 'r') as f:
         data = f.read()
         models = json.loads(data)['models']
         realms = json.loads(data)['realms']
         variables = json.loads(data)['variables']
         frequencies = json.loads(data)['frequencies']
         tables = json.loads(data)['tables']
         experiments = json.loads(data)['experiments']
         if project == 'CMIP5':
             families = json.loads(data)['families']
         if project == 'CMIP6':
             activities = json.loads(data)['activities']
             stypes = json.loads(data)['source_types']
             return models, realms, variables, frequencies, tables, experiments, activities, stypes
    
    return models, realms, variables, frequencies, tables, experiments, families 

def fix_model(project, models, invert=False):
    """
    Fix model name where file attribute is different from values accepted by facets

    >>> fix_model('CMIP5', ['CESM1(BGC)', 'CESM1-BGC'])
    ['CESM1(BGC)', 'CESM1(BGC)']

    >>> fix_model('CMIP5', ['CESM1(BGC)', 'CESM1-BGC'], invert=True)
    ['CESM1-BGC', 'CESM1-BGC']

    Args:
        project: Either 'CMIP5' or 'CMIP6'
        models: List of models to convert
        invert: Invert the conversion (so go from ``CESM1(BGC)`` to ``CESM1-BGC``)
    """
    project = project.upper()
    if project  == 'CMIP5':
        mfile = pkg_resources.resource_filename(__name__, 'data/'+project+'_model_fix.json')
        with open(mfile, 'r') as f:
            mdict = json.loads( f.read() )
        if invert:
            mfix = {v: k for k, v in mdict.items()}
        else:
            mfix = mdict
    return [ mfix[m] if m in mfix.keys() else m for m in models]


def call_local_query(s, project, oformat, **kwargs):
    ''' call local_query for each combination of constraints passed as argument, return datasets/files paths '''
    datasets = []
    paths = []
    if 'model' in kwargs.keys():
        kwargs['model'] = fix_model(project, kwargs['model'])
    combs = [dict(zip(kwargs, x)) for x in itertools.product(*kwargs.values())]
    for c in combs:
        datasets.extend( local_query(s,project=project,**c) ) 
    if oformat == 'dataset':
        for d in datasets:
            paths.append(d['pdir'])
    elif oformat == 'file':
        for d in datasets:
            paths.extend([d['pdir']+"/" + x for x in d['filenames']])
    return paths


def fix_path(path):
    '''Get path from query results and replace al33 output1/2 dirs to combined 
        and rr3 ACCESS "/files/" path to "/latest/"
    '''
    if '/al33/replicas/CMIP5/output' in path:
        return re.sub(r'replicas\/CMIP5\/output[12]?\/','replicas/CMIP5/combined/',path)
    elif '/al33/replicas/CMIP5/unsolicited' in path:
        return path.replace('unsolicited','combined')
    elif '/rr3/publications/CMIP5/output1/CSIRO-BOM' in path:
        dirs=path.split("/")
        var = dirs[-2].split("_")[0]
        return "/".join(dirs[0:-3]+['latest',var,dirs[-1]])
    else:
        return path

def and_filter(results, cols, fixed, **kwargs):
    ''' Filter query results to find all the simulations that have 
        all the different values passed for the attributes listed in cols.
        A simulation is defined by the attributes passed in the list fixed.
        :input: cols (list) the attributes for which we want all values to be present
        :input: fixed (list) are the attributes used to define a simulation (i.e. model/ensemble/version)
        :input: kwargs (dictionary) are the query constraints
        :return: query results and a list of dictionaries each representing a 'simulation'
                 that has all the requested values for "cols"
    '''
    tab = pandas.DataFrame(results)
    # if you want to select all the values for two or more columns
    # create a new column with their values paired to use for the aggregation
    if len(cols) >= 1 :
        tab['comb'] = list(zip(*[tab[c] for c in cols]))
    # list all combinations of cols attributes
        comb = list(itertools.product(*[kwargs[c] for c in cols]))
    # define the aggregation dictionary first
    # useful is a list of fields to retain in the table, the values
    # get added to final fields list only if in results.keys 
    useful =  set(['version', 'source_id', 'model', 'pdir','dataset_id',
              'cmor_table','table_id', 'ensemble', 'member_id']) - set(fixed)
    fields = ['comb'] + [f for f in useful if f in results[0].keys()]
    agg_dict = {k: set for k in fields}
    # group table data by the columns listed in fix_col i.e. model and ensemble
    # and aggregate rows with matching values creating a set for each including path and version
    # reset the table indexes
    d = (tab.groupby(fixed)
       .agg(agg_dict)
       .reset_index())
    # create a filter to select the rows where the lenght of the simulation combinations is
    # is equal to the number of "cols" combinations
    allvalues = (d['comb'].map(len) == len(comb) )
    # apply filter to table and return results as a dictionary
    selection=d[allvalues].to_dict('r')
    return selection


def matching(session, cols, fixed, project='CMIP5', local=True, **kwargs):
    ''' Call and_filter after executing local or remote query of passed constraints 
        :session: database session
        :project: ESGF project to search (cmip5/cmip6)
        :input: cols (list) the attributes for which we want all values to be present
        :input: fixed (list) are the attributes used to define a simulation (i.e. model/ensemble/version)
        :input: kwargs (dictionary) are the query constraints
        :return: output of and_filter: query results and a filter selection lists 
    '''

    results = []
    # use local search
    if local:
        msg = "There are no simulations stored locally"
        # perform the query for each variable separately and concatenate the results
        combs = [dict(zip(kwargs, x)) for x in itertools.product(*kwargs.values())]
        for c in combs:
            results.extend( search(session,project=project.lower(),**c) )
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
        response = esgf_query(query, fields, **kwquery)
        for row in response['response']['docs']:
            results.append({k:(v[0] if type(v)==list else v) for k,v in row.items()})

    # if nothing turned by query print warning and return
    if len(results) == 0:
        print(f'${msg} for ${kwargs}')
        return
    return results, and_filter(results, cols, fixed, **kwargs) 



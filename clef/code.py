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
from datetime import datetime
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



def cmip5(debug=False, distrib=True, replica=False, latest=True, oformat='dataset',**kwargs):
    """
    Search local database for CMIP5 files

    Constraints can be specified multiple times, in which case they are combined
    using OR: -v tas -v tasmin will return anything matching variable = 'tas' or variable = 'tasmin'.
    The --latest flag will check ESGF for the latest version available, this is the default behaviour
    """

    if debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger('sqlalchemy.engine').setLevel(level=logging.INFO)

    user=None
    connect(user=user)
    s = Session()

    project='CMIP5'

    terms = {}
 
    valid_constraints = [
        'ensemble',
        'experiment',
        'experiment_family',
        'institute',
        'model',
        'realm',
        'frequency',
        'cmor_table',
        'cf_standard_name',
        'variable']

    for key, value in kwargs.items():
        if key not in valid_constraints:
            print(f'Warning {key} is not a valid constraint it will be ignored')
        elif len(value) > 0:
           terms[key] = value

    subq = match_query(s, query=None,
            distrib= distrib,
            replica=replica,
            latest=(None if latest == 'all' else latest),
            project=project,
            **terms
            )

    # Make sure that if find_local_path does an all-version search using the
    # filename, the resulting project is still CMIP5 (and not say a PMIP file
    # with the same name)

    ql = find_local_path(s, subq, oformat=oformat)
    ql = ql.join(Path.c5dataset).filter(C5Dataset.project==project)
    results = kwargs 
    results['path'] = []
    for resp in ql:
        results['path'].append(resp[0])

    return results 

def cmip6(debug=False, distrib=True, replica=False, latest=True, oformat='dataset',**kwargs):
    """
    Search local database for CMIP6 files

    Constraints can be specified multiple times, in which case they are combined    using OR: -v tas -v tasmin will return anything matching variable = 'tas' or variable = 'tasmin'.
    The --latest flag will check ESGF for the latest version available, this is the default behaviour
    """

    if debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger('sqlalchemy.engine').setLevel(level=logging.INFO)

    user=None
    connect(user=user)
    s = Session()

    project='CMIP6'

    valid_constraints = [
        'member_id',
        'activity_id',
        'experiment_id',
        'sub_experiment_id',
        'institution_id',
        'source_id',
        'source_type',
        'realm',
        'frequency',
        'table_id',
        'variable_id',
        'grid_label',
        'cf_standard_name',
        'nominal_resolution'] 

    terms = {}

    # Add filters
    for key, value in dataset_constraints.items():
        if len(value) > 0:
            terms[key] = value

    subq = match_query(s, query=None,
            distrib=distrib,
            replica=replica,
            latest=(None if latest == 'all' else latest),
            project=project,
            **terms
            )

    # Make sure that if find_local_path does an all-version search using the
    # filename, the resulting project is still CMIP5 (and not say a PMIP file
    # with the same name)
    ql = find_local_path(s, subq, oformat=oformat)
    ql = ql.join(Path.c6dataset).filter(C6Dataset.project==project)

    results = kwargs 
    results['path'] = []
    for resp in ql:
        results['path'].append(resp[0])
    return results 
 
def search(session, project='cmip5', **kwargs):
    """
    This call the local query when integrated in python script before running query checks
    that the arguments names and values are correct and change model name where necessary
    """
    args = check_keys(project, kwargs)
    check_values(project, args)
    args = fix_model(project, args)
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
    df['pdir'] = df['path'].map(os.path.dirname)
    df['filename'] = df['path'].map(os.path.basename)
    res = df.groupby(['pdir'])
    results=[]
    cols = [x for x in list(df) if x not in ['filename','path','period'] ]
    for g,v in res.groups.items():
        gdict={}
        gdict['filenames'] = df['filename'].iloc[list(v)].tolist()
        gdict['periods'] = df['period'].iloc[list(v)].tolist()
        gdict['fdate'], gdict['tdate'] = convert_period(gdict['periods'])
        for c in cols:
            gdict[c] = df[c].iloc[list(v)].unique()[0]
        results.append(gdict)

    return results

def convert_period(nranges):
    """
    Convert a list of NumericRange period to a from-date,to-date separate values
    """
    try:
        lower, higher = nranges[0].lower, nranges[0].upper
        for nr in nranges[1:]:
            low, high = nr.lower, nr.upper
            lower = min(low,lower)
            higher = max(high, higher)
    except:
        lower, higher = None, None
    return lower, higher


def check_keys(project, kwargs):
    """
    Check that arguments keys passed to search are valid, if not print warning and exit
    """
    # load dictionary to check arguments keys are valid
    # valid_keys has as keys tuple of all valid arguments and as values dictionaries 
    # representing the corresponding facet for CMIP5 and CMIP6
    # ex. ('variable', 'variable_id', 'v'): {'cmip5': 'variable', 'cmip6': 'variable_id'}
    with open('clef/data/valid_keys.json', 'r') as f:
         data = json.loads(f.read()) 
    valid_keys = {v[project]: k.split(":") for k,v in data.items() if v[project] != 'NA'}
    # rewrite kwargs with the right facet name
    args = {}
    for key,value in kwargs.items():
        facet = [k for k,v in valid_keys.items() if key in v]
        if facet==[]:
            print(f"Warning {key} is not a valid constraint name")
            print(f"Valid constraints are:\n{valid_keys.values()}")
            sys.exit()
        else:
            args[facet[0]] = value
    return args

def check_values(project, args):
    """
    Check that arguments values passed to search are valid, if not print warning and exit
    """
    # load dictionaries to check arguments values are valid
    if project == 'cmip5':
        models, realms, variables, frequencies, tables = load_vocabularies('CMIP5')
    elif project == 'cmip6':
        models, realms, variables, frequencies, tables, activities, stypes = load_vocabularies('CMIP6')
    else:
        print(f'Search for {project} not yet implemented')
        sys.exit()
            
    #for k,v in args.items():
    #     if models: 
    #    args[valid_key[ 
    return args


def load_vocabularies(project):
    ''' '''
    vfile = pkg_resources.resource_filename(__name__, 'data/'+project+'_validation.json')
    mfile = pkg_resources.resource_filename(__name__, 'data/'+project+'_validation.json')
    with open(vfile, 'r') as f:
         data = f.read()
         models = json.loads(data)['models']
         realms = json.loads(data)['realms']
         variables = json.loads(data)['variables']
         frequencies = json.loads(data)['frequencies']
         tables = json.loads(data)['tables']
         #experiments = json.loads(data)['experiments'] 
         if project == 'CMIP6':
             activities = json.loads(data)['activities']
             stypes = json.loads(data)['source_types']
             return models, realms, variables, frequencies, tables, activities, stypes
    
    return models, realms, variables, frequencies, tables 

def fix_model(project, args):
    """
    Fix model name where file attribute is different from values accepted by facets
    """
    project = project.upper()
    if project  == 'CMIP5':
        mfile = pkg_resources.resource_filename(__name__, 'data/'+project+'_model_fix.json')
        with open(mfile, 'r') as f:
            mfix = json.loads( f.read() )
        if args['model'] in mfix.keys():
            args['model'] = mfix[args['model']]
    return args

def call_local_query(s, project, oformat, **kwargs):
    ''' call local_query for each combination of constraints passed as argument, return datasets/files paths '''
    datasets = []
    paths = []
    combs = [dict(zip(kwargs, x)) for x in itertools.product(*kwargs.values())]
    for c in combs:
        c = fix_model(project, c)
        datasets.extend( local_query(s,project=project,**c) ) 
    if oformat == 'dataset':
        for d in datasets:
            paths.append(d['pdir'])
    elif oformat == 'file':
        for d in datasets:
            paths.extend([d['pdir']+x for x in d['filenames']])
    return paths

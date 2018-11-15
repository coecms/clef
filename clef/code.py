#!/usr/bin/env python
# Copyright 2018 ARC Centre of Excellence for Climate Extremes
# author: Scott Wales <paola.petrelli@utas.edu.au>
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
from .model import Path, c5_metadata_dataset_link, c6_metadata_dataset_link, ExtendedMetadata
from .model import C5Dataset, C6Dataset
from .exception import ClefException
from datetime import datetime
from sqlalchemy import any_, or_
from sqlalchemy.orm import aliased
from itertools import groupby
import logging
import sys
import os
import json
import pkg_resources


def warning(message):
    print("WARNING: %s"%message, file=sys.stderr)

def load_vocabularies(project):
    vfile = pkg_resources.resource_filename(__name__, 'data/'+project+'_validation.json')
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
    

#def cmip5_args(f):
#    models, realms, variables, frequencies, tables = load_vocabularies('CMIP5')
#    constraints = [
#        tion('--experiment', '-e', multiple=True, help="CMIP5 experiment: piControl, rcp85, amip ..."),
#        click.option('--experiment_family',multiple=True, help="CMIP5 experiment family: Decadal, RCP ..."),
#        click.option('--model', '-m', multiple=True, type=click.Choice(models),  metavar='x', 
#                      help="CMIP5 model acronym: ACCESS1.3, MIROC5 ..."),
#        click.option('--table', '--mip', '-t', 'cmor_table', multiple=True, type=click.Choice(tables) ),
#                      #help="CMIP5 CMOR table: Amon, day, Omon ..."),
#        click.option('--variable', '-v', multiple=True, type=click.Choice(variables), metavar='x',
#                      help="Variable name as shown in filanames: tas, pr, sic ... "),
#        click.option('--ensemble', '--member', '-en', 'ensemble', multiple=True, help="CMIP5 ensemble member: r#i#p#"),
#        click.option('--frequency', 'time_frequency', multiple=True, type=click.Choice(frequencies) ), 
                     # help="Frequency"),
#        click.option('--realm', multiple=True, type=click.Choice(realms) ),
                     # help="CMIP5 realm"),
#        click.option('--institution', 'institute', multiple=True, help="Modelling group institution id: MIROC, IPSL, MRI ...")
#    ]
#    return f

#def common_args(f):
#    constraints = [
#        click.option('--cf_standard_name',multiple=True, help="CF variable standard_name, use instead of variable constraint "),
#        click.option('--format', 'oformat', type=click.Choice(['file','dataset']), default='dataset',
#                     help="Return output for datasets (default) or individual files"),
#        click.option('--latest/--all-versions', 'latest', default=True,  
#                     help="Return only the latest version or all of them. Default: --latest"),
#        click.option('--replica/--no-replica', default=False, 
#                     help="Return both original files and replicas. Default: --no-replica"),
#        click.option('--distrib/--no-distrib', 'distrib', default=True, 
#                     help="Distribute search across all ESGF nodes. Default: --distrib"),
#        click.option('--debug/--no-debug', default=False,
#                     help="Show debug output. Default: --no-debug")
#    ]
#    return f

#def cmip6_args(f):
# 
#    models, realms, variables, frequencies, tables, activities, stypes = load_vocabularies('CMIP6')
#    constraints = [
#        ('--activity', '-mip', 'activity_id', multiple=True, type=click.Choice(activities) ) ,
#                     #help="CMIP6 MIP or project id"),
#        ('--experiment', '-e', 'experiment_id', multiple=True, help="CMIP6 experiment, list of available depends on activity"),
#        ('--source_type',multiple=True, type=click.Choice(stypes) ),
#                     #help="Model configuration"),
#        ('--table', '-t', 'table_id', multiple=True, type=click.Choice(tables), metavar='x',
#                     help="CMIP6 CMOR table: Amon, SIday, Oday ..."),
#        ('--model', '--source_id','-m', 'source_id', multiple=True, type=click.Choice(models),  metavar='x',
#                     help="CMIP6 model id: GFDL-AM4, CNRM-CM6-1 ..."),
#        ('--variable', 'variable_id', '-v', multiple=True, type=click.Choice(variables),  metavar='x', 
#                     help="CMIP6 variable name as in filenames"),
#        ('--member', '-mi', 'member_id', multiple=True, help="CMIP6 member id: <sub-exp-id>-r#i#p#f#"),
#        ('--grid', '--grid_label', '-g', 'grid_label', multiple=True, help="CMIP6 grid label: i.e. gn for the model native grid"),
#        ('--resolution', '--nominal_resolution','-nr' , 'nominal_resolution', multiple=True, help="Approximate resolution: '250 km', pass in quotes"),
#        ('--frequency',multiple=True, type=click.Choice(frequencies) ),
                     # help="Frequency"),
#        ('--realm', multiple=True, type=click.Choice(realms) ),
                     # help="CMIP6 realm"),
#        ('--sub_experiment_id', '-se', multiple=True, help="Only available for hindcast and forecast experiments: sYYYY"),
#        ('--variant_label', '-vl', multiple=True, help="Indicates a model variant: r#i#p#f#"),
#        ('--institution', 'institution_id', multiple=True, help="Modelling group institution id: IPSL, NOAA-GFDL ..."),
#    ]
#    return f

def cmip5(debug=False, distrib=True, replica=False, latest=True, oformat='dataset',**kwargs):
    """
    Search local database for CMIP5 files

    Constraints can be specified multiple times, in which case they are combined    using OR: -v tas -v tasmin will return anything matching variable = 'tas' or variable = 'tasmin'.
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
 

def local_query(session,project='cmip5',**kwargs):
    """
    """
    # create empty list for results dictionaries
    # each dict will represent a file matching the constraints
    results=[]
    if project == 'cmip5':
        # separate var from other 
        var = kwargs.pop('variable')
    cmip={'cmip5': [c5_metadata_dataset_link, C5Dataset],
          'cmip6': [c6_metadata_dataset_link, C6Dataset]}
        
    out=session.query(cmip[project][0],cmip[project][1]).join(cmip[project][1]).filter_by(**kwargs)
    if project == 'cmip5':
        out1=out.join(Path).join(ExtendedMetadata).filter(ExtendedMetadata.variable == var)
    else:
        out1=out.join(Path).join(ExtendedMetadata).filter()
    for o in out1.all():
        row=session.query(Path).join(cmip[project][0]).filter(Path.id == o.file_id).one_or_none()
        if not row:
            print(f'Warning there is a {project} file without path!')
            sys.exit()
        result = row_to_dict(row, project) 
        results.append(result)
    return results

def row_to_dict(row, project): 
    """
    """
    if project == 'cmip5':
        cdata =  row.c5dataset[0]
    else:
        cdata =  row.c6dataset[0]
    result={}
    for col in cdata.__table__.columns:
        if col.name == 'frequency' and project == 'cmip5': 
            result[col.name] = cdata.__getattribute__('time_frequency') 
        else:
            result[col.name] = cdata.__getattribute__(col.name) 
    for col in ['version','period','variable']:
        result[col] = row.extended[0].__getattribute__(col) 
    dirs = row.path.split("/")
    result['path'] = "/".join(dirs[:-1])
    result['filename'] = dirs[-1]
    result.pop('dataset_id')
    #result.update(row.c5dataset[0].__dict__)
    #result.update(row.extended[0].__dict__)
    return result

def files_to_dataset(results): 
    """
    """
    datasets=[]
    groups = []
    keyfunc = lambda x: x['path']
    data = sorted(results, key=keyfunc)
    for k, g in groupby(data, key=keyfunc):
        groups.append(list(g))      # Store group iterator as a list
    for g in groups:
        #for g in group:
            d = {k: v for k,v in g[0].items()}
            d['filenames'] = []
            #d['periods'] = []
            periods = []
            d.pop('filename')
            d.pop('period')
            for ds in g:
                d['filenames'].append(ds['filename'])
                #d['periods'].append(ds['period'])
                periods.append(ds['period'])
            #d['fdate'], d['tdate'] = convert_period(d['periods'])
            d['fdate'], d['tdate'] = convert_period(periods)
            datasets.append(d)

    return datasets

def convert_period(nranges):
    """
    Convert a list of NumericRange period to a from-date,to-date separate values
    """
    lower, higher = nranges[0].lower, nranges[0].upper
    for nr in nranges[1:]:
        low, high = nr.lower, nr.upper
        lower = min(low,lower)
        higher = max(high, higher)
    return lower, higher

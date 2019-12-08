#!/usr/bin/env python
# Copyright 2019 ARC Centre of Excellence for Climate Extremes
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


import json
import re
import pkg_resources

from calendar import monthrange
from datetime import datetime, timedelta

from .exception import ClefException


def get_version(path):
    """Retrieve version from path if not available in MAS

    Args:
        path (str): data directory path

    Returns:
        string of version extracted from path or None

    """
    mo = re.search(r'\d{8}', path)
    if mo:
        return  mo.group()
    else:
        return  None 


def convert_periods(nranges):
    """Convert period Numeric ranges to dates intervals

    Args:
        nranges (list of NumericRange): list of files temporal intervals

    Returns:
        periods (list of tuples): ranges of file dates as string

    """ 
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


def get_range(periods):
    """Find from-date,to-date for simulation from list of file periods

    Args:
        periods (list of tuples): ranges of file dates as string

    Returns:
        from_date, to_date (string): or None, None

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


def time_axis(periods,fdate,tdate):
    """Check that files constitute a contiguos time axis

    Args:

      periods (list of tuples): ranges of file dates as string
      fdate (str): from date
      tdate (str): to_date

    Returns:
        True or False

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
    """Define valid arguments keys based on project

    Args:
        project (str): data project

    Returns:
        valid_keys (dict): with valid keys for project facets

    """
    # valid_keys.json is a dictionary where the keys are tuple of all valid arguments
    # and the values represent the corresponding facet for CMIP5 and CMIP6
    # ex. ('variable', 'variable_id', 'v'): {'CMIP5': 'variable', 'CMIP6': 'variable_id'}
    fkeys = pkg_resources.resource_filename(__name__, 'data/valid_keys.json')
    with open(fkeys, 'r') as f:
         data = json.loads(f.read())
    try:
        valid_keys = {v[project]: k.split(":") for k,v in data.items() if v[project] != 'NA'}
    except KeyError:
        raise ClefException(f"Keys validation not defined for project: {project}")
    return valid_keys


def get_facets(project):
    """Return dictionary of facets to use based on project

    Args:
        project (str): data project

    Returns:
        facets (dictionary): project facets

    """
    facets =  {'CMIP6': {}, 'CMIP5': {}}
    ffacets = pkg_resources.resource_filename(__name__, 'data/facets.json')
    with open(ffacets, 'r') as f:
         data = json.loads(f.read()) 
    try:
        new_keys = ['mip','pr', 'e', 'f', 'gr', 'inst', 'era', 'res',  'prod',
                    'r', 'm', 'mtype', 'se', 't', 'v', 'vl', 'en', 'ef', 'cf']
        #for x,y in zip(new_keys, [x for x in data.keys()]):
        #    facets['CMIP6'][x] = y
        facets['CMIP6'] = {k:v for k,v in zip(new_keys, [x for x in data.keys()])}
        facets['CMIP5'] = {k:v for k,v in zip(new_keys, [x for x in data.values()])}
    except KeyError:
        raise ClefException(f"Keys validation not defined for project: {project}")
    return facets[project]


def check_keys(valid_keys, kwargs):
    """Check that arguments keys passed to search are valid, if not print warning and exit

    Args:
        valid_keys (dict): with valid keys for project facets
        kwargs (dict): query constraints

    Returns:
        args (dict): query constraints with accepted facet names

    """ 
    # load dictionary to check arguments keys are valid
    # rewrite kwargs with the right facet name
    args = {}
    for key,value in kwargs.items():
        facet = [k for k,v in valid_keys.items() if key in v]
        if facet==[]:
            raise ClefException(
                f"Warning {key} is not a valid constraint name"
                f"Valid constraints are:\n{valid_keys.values()}")
        else:
            args[facet[0]] = value
    return args


def check_values(args, project, vocabularies):
    """Check that arguments values passed to search are valid, if not print warning and exit

    Args:
        args (dict): query constraints
        project (str): data project
        vocabularies (dict of lists): {facet: valid values}

    Returns:

    """
    # load dictionaries to check arguments values are valid
    #if project == 'CMIP5':
    #    model, realm, variable, frequency, table, experiment, experiment_family, attributes = vocabularies
    #elif project == 'CMIP6':
    #    source_id, realm, variable_id, frequency, table_id, experiment_id, activity_id, source_type, attributes = vocabularies
    if project not in ['CMIP5', 'CMIP6']:
        #raise NotImplementedError(f'Search for {project} not yet implemented')
        raise ClefException(f'Search for {project} not yet implemented')
    facets = [k for k in vocabularies.keys()]
    for k,v in args.items():
        if k in facets and v not in vocabularies[k]:
            raise ClefException(f'"{v}" is not a valid value for the facet "{k}" in project {project}')
    return True


def load_vocabularies(project):
    """Load project vocabularies from json file.

    Load from project json data files all accepted values for facets.

    Args:
        project (str): data project

    Returns:
        a series of lists (list): one for each facets, elements are accepted values 

    """
    project = project.upper()
    vfile = pkg_resources.resource_filename(__name__, 'data/'+project+'_validation.json')
    with open(vfile, 'r') as f:
         data = f.read()
         vocab = json.loads(data)
        # models = json.loads(data)['models']
        # realms = json.loads(data)['realms']
        # variables = json.loads(data)['variables']
        # frequencies = json.loads(data)['frequencies']
        # tables = json.loads(data)['tables']
        # experiments = json.loads(data)['experiments']
        # attributes = json.loads(data)['attributes']
        # if project == 'CMIP5':
        #     families = json.loads(data)['families']
        # if project == 'CMIP6':
        #     activities = json.loads(data)['activities']
        #     stypes = json.loads(data)['source_types']
        #     return models, realms, variables, frequencies, tables, experiments, activities, stypes, attributes
    #return models, realms, variables, frequencies, tables, experiments, families, attributes
    return vocab


def fix_model(project, models, invert=False):
    """Fix model name where file attribute is different from values accepted by facets

    >>> fix_model('CMIP5', ['CESM1(BGC)', 'CESM1-BGC'])
    ['CESM1(BGC)', 'CESM1(BGC)']

    >>> fix_model('CMIP5', ['CESM1(BGC)', 'CESM1-BGC'], invert=True)
    ['CESM1-BGC', 'CESM1-BGC']

    Args:

        project (str): data project
        models (list) models to convert
        invert (bool): Invert the conversion (so go from ``CESM1(BGC)`` to ``CESM1-BGC``)

    """
    project = project.upper()
    if project  == 'CMIP5':
        mfile = pkg_resources.resource_filename(__name__, 'data/'+project+'_model_fix.json')
        with open(mfile, 'r') as f:
            mdict = json.loads(f.read())
        if invert:
            mfix = {v: k for k, v in mdict.items()}
        else:
            mfix = mdict
    return  [mfix[m] if m in mfix.keys() else m for m in models]


def fix_path(path, latest):
    """Get path from query results and replace al33 output1/2 dirs to combined
        and rr3 ACCESS "/files/" path to "/latest/"

    Args:

    """
    if '/al33/replicas/CMIP5/output' in path:
        return re.sub(r'replicas\/CMIP5\/output[12]?\/','replicas/CMIP5/combined/',path)
    elif '/al33/replicas/CMIP5/unsolicited' in path:
        return path.replace('unsolicited','combined')
    elif '/rr3/publications/CMIP5/output1/CSIRO-BOM' in path and latest:
        dirs=path.split("/")
        var = dirs[-2].split("_")[0]
        return "/".join(dirs[0:-3]+['latest',var,dirs[-1]])
    else:
        return path


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


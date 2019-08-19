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

from clef.code import *
#from code_fixtures import session
from code_fixtures import * 
import pytest

# Tests for the basic list queries

def present_query(*args, **kwags):
    """
    A query returning something that is in the DB
    """
    response =  {
            'responseHeader': {'params': {'rows': 1}},
            'response': {
                'numFound': 1,
                'docs': [{
                    'id': 'abcde',
                    'checksum': ['6cf73c8c375f0005fa6dea53608a660e'],
                    'title': 'clt_3hr_ACCESS1-3_1pctCO2_r1i1p1_036001010130-036412312230.nc',
                    'version': '1',
                    'latest': 'true',
                    'score': 1.0,
                    'dataset_id': 'dataset_bar|example.com',
                    }],
                }
            }
    return response

def test_check_values(c5_kwargs, c5_vocab):
    args = check_values(c5_vocab, 'CMIP5', c5_kwargs)
    assert args == c5_kwargs 
    bad_arg=c5_kwargs.copy()
    bad_arg['experiment'] = 'dummy'
    with pytest.raises(ClefException):
        args = check_values(c5_vocab, 'CMIP5', bad_arg)

def test_check_load_vocabularies():
    project = 'CMIP5'
    vocab = load_vocabularies(project)
    args = check_values(vocab, project, {'variable':'tas'})
    assert args['variable'] == 'tas'

    project = 'CMIP6'
    vocab = load_vocabularies(project)
    args = check_values(vocab, project, {'variable_id':'tas'})
    assert args['variable_id'] == 'tas'

def test_check_keys(c5_kwargs,c5_keys):
    args = check_keys(c5_keys, c5_kwargs)
    assert args == {'model': 'INM-CM4', 'experiment': 'rcp85', 'variable': 'tas', 
                    'cmor_table': 'Amon', 'time_frequency': 'mon', 'institute': 'MIROC',
                    'experiment_family': 'RCP', 'ensemble': 'r1i1p1'}
    bad_arg=c5_kwargs.copy()
    bad_arg['activity_id'] = 'dummy'
    with pytest.raises(ClefException):
        args = check_keys(c5_keys, bad_arg)

def test_get_keys():
    with pytest.raises(ClefException):
        keys = get_keys('dummy')

def test_fix_model():
    models = fix_model('cmip5', ['INM-CM4'], invert=True) 
    assert models == ['inmcm4']
    arg_model = ['CESM1-BGC', 'ACCESS1-0']
    models = fix_model('CMIP5', arg_model) 
    assert models == ['CESM1(BGC)', 'ACCESS1.0']

def test_convert_periods(nranges, periods, empty):
    res1 = convert_periods(nranges,'mon')
    assert res1 == periods[0]
    assert convert_periods(empty,'mon') == ([]) 

    nranges2 = nranges.copy()
    nranges2.append(None)
    res2 = convert_periods(nranges2, 'mon')
    assert res2 == res1

def test_time_axis(periods):
    #test contiguos axis monthly frequency 
    assert time_axis(periods[0],'20060101','21001231') == True 
    #test contiguos axis, 2 files, daily frequency 
    bad_list=periods[0][0:2]
    assert time_axis(bad_list,'20050101','20050228') == False 

def test_get_range(periods, empty):
    assert get_range(periods[0]) == ('20060101', '21001231') 
    assert get_range(empty) == (None, None) 

def test_fix_path():
    dir1 = '/g/data/rr3/publications/CMIP5/output1/CSIRO-BOM/more/files/tas_20120115/'
    dir2 = '/g/data/rr3/publications/CMIP5/output1/CSIRO-QCCCE/more/files/tas_20110518/'
    dir3 = '/g/data/al33/replicas/CMIP5/output1/more/v20120316/tas/'
    dir4 =  dir3.replace('output1', 'unsolicited')
    fname = 'name.nc'
    assert fix_path(dir1) == '/g/data/rr3/publications/CMIP5/output1/CSIRO-BOM/more/latest/tas/'
    assert fix_path(dir1+fname) == '/g/data/rr3/publications/CMIP5/output1/CSIRO-BOM/more/latest/tas/name.nc'
    assert fix_path(dir2) == '/g/data/rr3/publications/CMIP5/output1/CSIRO-QCCCE/more/files/tas_20110518/'
    assert fix_path(dir3) == '/g/data/al33/replicas/CMIP5/combined/more/v20120316/tas/'
    assert fix_path(dir3+fname) == '/g/data/al33/replicas/CMIP5/combined/more/v20120316/tas/name.nc'
    assert fix_path(dir4) == '/g/data/al33/replicas/CMIP5/combined/more/v20120316/tas/'

def test_and_filter(local_results, remote_results):
    kwargs = {'experiment': ['exp1','exp2'], 'variable': ['tas','pr'],
              'cmor_table': ['Amon'], 'ensemble': ['r1i1p1','r2i1p1']}
    # first selection should return mod1/exp1/r1i1p1
    # mod2/exp1/r1i1p1 
    # mod2/exp2/r1i1p1 
    selection = and_filter(local_results, ['variable'],['model','ensemble','experiment'], **kwargs)
    assert selection[0]['comb'] == { ('tas', ), ('pr', )} 
    assert len(selection) == 3
    selection = and_filter(local_results, ['variable','experiment'],
                ['model','ensemble'], **kwargs)
    assert selection[0]['comb'] == { ('tas', 'exp1'), ('pr', 'exp1'),
                                     ('tas', 'exp2'), ('pr', 'exp2')} 
    assert len(selection) == 1 
    # testing remote CMIP6 query results
    kwargs = {'experiment_id': ['exp1','exp2'], 'variable_id': ['tas','pr'],
              'table_id': ['Amon'], 'member_id': ['r1i1p1f1','r2i1p1f1']}
    selection = and_filter(remote_results, ['variable_id'],
                ['source_id','member_id','experiment_id'], **kwargs)
    assert selection[0]['comb'] == { ('tas', ), ('pr', )} 
    assert len(selection) == 4 
    dids=[]
    for s in selection: 
        dids.extend(s['dataset_id']) 
    print(dids)
    assert 'mod1.exp1.Amon.r2i1p1f1.pr.v1' not in dids
    assert 'mod1.exp1.Amon.r1i1p1f1.pr.v1' in dids
    selection = and_filter(remote_results, ['variable_id','experiment_id'],
                           ['source_id','member_id'], **kwargs)
    assert selection[0]['comb'] == { ('tas', 'exp1'), ('pr', 'exp1'),
                                     ('tas', 'exp2'), ('pr', 'exp2')} 
    assert len(selection) == 1 
    selection = and_filter(remote_results, ['variable_id'],
                ['source_id','member_id','experiment_id','version'], **kwargs)
    models = [s['source_id'] for s in selection] 
    assert 'mod2' not in models
    assert len(selection) == 2 


@pytest.mark.production
def test_search(session):
    with pytest.raises(ClefException):
        search(session, project='cmip5', model='bad')
    with pytest.raises(ClefException):
        search(session, project='CMIP5', foo='blarg')

    facets = {
        'experiment':'historical',
        'cmor_table':'Amon',
        'ensemble':'r1i1p1',
        'variable':'tas'
    }

    r0 = search(session, project='cmip5', model='ACCESS1.0', **facets)

@pytest.mark.production
def test_search_results(session):
    facets = {
        'experiment':'historical',
        'cmor_table':'Amon',
        'ensemble':'r1i1p1',
        'variable':'tas'
    }

    r0 = search(session, project='cmip5', model='ACCESS1.0', **facets)
    assert len(r0) == 1, "Only one result"
    assert r0[0]['model'] == 'ACCESS1.0', "Model matches input"

    r1 = search(session, project='cmip5', model='ACCESS1-0', **facets)
    assert len(r1) == len(r0), "Same result with filtered name"
    assert r1[0]['model'] == 'ACCESS1.0', "Model is cleaned"

    # No variable constraint
    facets.pop('variable')
    r2 = search(session, project='cmip5', model='ACCESS1-0', **facets)
    assert len(r2) == 48

    r3 = search(session, project='cmip6', model='AWI-CM-1-1-MR',
                experiment='historical', variable='uas', cmor_table='3hr')
    assert r3[0]['pdir'] == '/g/data1b/oi10/replicas/CMIP6/CMIP/AWI/AWI-CM-1-1-MR/historical/r1i1p1f1/3hr/uas/gn/v20181218'

def test_matching(session):
    facets = {
        'experiment':['historical'],
        'cmor_table':'Amon',
        'ensemble':'r1i1p1',
        'variable': ['x'],
    }
    # Errors should print a message and return 'None'
    r = matching(session, ['variable','experiment'],['model','ensemble'], **facets)
    assert r is None

def test_get_version():
    assert get_version('/g/data/inst/model/var/v20130405') == 'v20130405'
    assert get_version('/g/data/inst/model/var/v20130405/tas/files') == 'v20130405'
    assert get_version('/g/data/inst/model/var/noversionhere/tas/files') == None


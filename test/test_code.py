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
    args = check_values(c5_vocab, 'cmip5', c5_kwargs)
    assert args == c5_kwargs 
    bad_arg=c5_kwargs.copy()
    bad_arg['experiment'] = 'dummy'
    with pytest.raises(SystemExit):
        args = check_values(c5_vocab, 'cmip5', bad_arg)

def test_check_keys(c5_kwargs,c5_keys):
    args = check_keys(c5_keys, c5_kwargs)
    assert args == {'model': 'INM-CM4', 'experiment': 'rcp85', 'variable': 'tas', 
                    'cmor_table': 'Amon', 'time_frequency': 'mon', 'institute': 'MIROC',
                    'experiment_family': 'RCP', 'ensemble': 'r1i1p1'}
    bad_arg=c5_kwargs.copy()
    bad_arg['activity_id'] = 'dummy'
    with pytest.raises(SystemExit):
        args = check_keys(c5_keys, bad_arg)

#def test_fix_model(c5_kwargs):
#    args = fix_model('cmip5', c5_kwargs) 
#    assert args['model'] == 'inmcm4'

def test_convert_periods(nranges, periods, empty):
    res1 = convert_periods(nranges,'mon')
    assert res1 == periods[0]
    assert convert_periods(empty,'mon') == ([]) 

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
    dir2 = '/g/data/rr3/pubblications/CMIP5/output1/CSIRO-QCCCE/more/files/tas_20110518/'
    dir3 = '/g/data/al33/replicas/CMIP5/output1/more/v20120316/tas/'
    dir4 =  dir3.replace('output1', 'unsolicited')
    fname = 'name.nc'
    assert fix_path(dir1) == '/g/data/rr3/publications/CMIP5/output1/CSIRO-BOM/more/latest/tas/'
    assert fix_path(dir1+fname) == '/g/data/rr3/publications/CMIP5/output1/CSIRO-BOM/more/latest/tas/name.nc'
    assert fix_path(dir2) == '/g/data/rr3/pubblications/CMIP5/output1/CSIRO-QCCCE/more/files/tas_20110518/'
    assert fix_path(dir3) == '/g/data/al33/replicas/CMIP5/combined/more/v20120316/tas/'
    assert fix_path(dir3+fname) == '/g/data/al33/replicas/CMIP5/combined/more/v20120316/tas/name.nc'
    assert fix_path(dir4) == '/g/data/al33/replicas/CMIP5/combined/more/v20120316/tas/'


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

def test_fix_model(c5_kwargs):
    args = fix_model('cmip5', c5_kwargs) 
    assert args['model'] == 'inmcm4'

def test_convert_periods(nranges, periods, dates, empty):
    res1, res2 = convert_periods(nranges,'mon')
    assert res1 == periods[0]
    assert len(res2) == len(dates[2]) 
    #for dti in res2:
    #    assert dti.all() in dates[2]
    #assert convert_periods(nranges,'mon') == (periods[0], dates[2]) 
    #assert convert_periods(empty,'mon') == (None, None) 

def test_time_axis(dates, empty):
    #test contiguos axis monthly frequency 
    assert time_axis(dates[2],'mon','20060101','21001231') == True 
    #test contiguos axis, 2 files, daily frequency 
    assert time_axis(dates[1],'day','20050101','20050228') == True 
    #test contiguos axis, 1 file, daily frequency 
    assert time_axis(dates[0],'day','20050101','20050228') == True 
    #test non-contiguos axis, monthly frequency 
    assert time_axis(dates[3],'mon','20060101','21001231') == False 
    #assert time_axis(empty) == False 

def test_get_range(periods, empty):
    assert get_range(periods[0]) == ('20060101', '21001231') 
    assert get_range(empty) == (None, None) 

#!/usr/bin/env python
# Copyright 2018 ARC Centre of Excellence for Climate Extremes 
# author: Scott Wales <scott.wales@unimelb.edu.au>
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

from clef.db_noesgf import *
from clefdb_fixtures import session

# Tests for the basic list queries

def test_datasets(session):
    assert session.dsets().sort() == ['DS1 v1.0 (netcdf)', 'DS1 v2.0 (netcdf)', 'DS2 v1.0 (netcdf)', 'DS2 v1.0 (HDF5)'].sort()

def test_variables(session):
    assert session.standard_names().sort() == ['air_temperature', 'rainfall_rate'].sort()

def test_vars_names(session):
    assert session.vars_names().sort() == ['ta', 'prec', 'T', 'p'].sort()

def test_cmor_names(session):
    assert session.cmor_names().sort() == ['ta', 'pr'].sort()

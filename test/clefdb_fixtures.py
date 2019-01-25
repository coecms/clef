#!/usr/bin/env python
"""
file:   test/clefdb_fixtures.py
author: Paola Petrelli <paola.petrelli@utas.edu.au>
Copyright 2018 ARC Centre of Excellence for Climate Systems Science
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import pytest
from clef import collections 
from clef.db_noesgf import Dataset, Variable
from sqlalchemy.orm.exc import NoResultFound
from datetime import date

def insert_unique(db, klass, **kwargs):
    """
    Insert an item into the DB if it can't be found
    """
    try:
        value = db.query(klass).filter_by(**kwargs).one()
    except NoResultFound:
        value = klass(**kwargs)
        db.add(value)
        db.commit()
    return value

def retrieve_item(db, klass, **kwargs):
    """
    Retrieve an item into the DB if it can be found
    """
    try:
        value = db.query(klass).filter_by(**kwargs).one()
    except NoResultFound:
        print( "Cannot find fixture with ", kwargs)
    return value


#def add_dataset_item(db, dataset_id, **kwargs):
#name, version, format, drs, filename,
#                     updated_on):
#    """
#    Add a new test dataset item to the DB
#    """
#    dataset = insert_unique(db, Version,**kwargs)
 #   dataset = insert_unique(db, Dataset,
 #           dataset_id = dataset_id,
 #           name       = name,
 #           path        = path,
 #   return version.id



@pytest.fixture(scope="module")
#def session(request, tmpdir_factory):
def session(request):
    session = collections.connect('sqlite:///:memory:')

    #dira = tmpdir_factory.mktemp('a')
    #dirb = tmpdir_factory.mktemp('b')

    # Create some example entries
    db = session.session
    added_on=date.today()
    # define some datasets
    ds1 = insert_unique(db, Dataset,
        name   = 'DS1',
        version      = '1.0',
        fileformat = 'netcdf',
        drs       = '/disk/data/DS1/v1/<frequency>/<year`>/',
        filename   = '<variable>_DS1_<fdate>_<todate>',
        access     = 'group x',
        manager    = 'someone@example.com',
        reference  = 'url')
    ds2 = insert_unique(db, Dataset,
        name   = 'DS1',
        version      = '2.0',
        fileformat = 'netcdf',
        drs       = '/disk/data/DS1/v2/<frequency>/<year`>/',
        filename   = '<variable>_DS1_<fdate>_<todate>',
        access     = 'group x',
        manager    = 'someone@example.com',
        reference  = 'url')
    ds3 = insert_unique(db, Dataset,
        name   = 'DS2',
        version      = '1.0',
        fileformat = 'HDF5',
        drs       = '/disk/data/DS2/<stream>/<grid>/<year`>/',
        filename   = '<variable>_DS2_<fdate>_<todate>',
        access     = 'group y',
        manager    = 'someone@example.com',
        reference  = 'url')
    ds1id = ds1.id
    ds2id = ds2.id
    ds3id = ds3.id
    # define some variables
    var1_1 = insert_unique(db, Variable,
        dataset_id = ds1id,
        name        = 'ta',
        long_name   = 'temperature ...',
        standard_name   = 'air_temperature',
        cmor_name  = 'ta',
        units      = 'K',
        levels     = '1000 900 800 500 200 0', 
        grid     = 'NA', 
        frequency     = '6hr', 
        updated_on  = added_on,
        fdate  = '19790101',
        tdate  = '20180831')
    var1_2 = insert_unique(db, Variable,
        dataset_id = ds1id,
        name        = 'p',
        long_name   = 'precipitation ...',
        standard_name   = 'rainfall_rate',
        cmor_name  = 'pr',
        units      = 'mm day-1',
        levels     = '1000 900 800 500 200 0', 
        grid     = 'NA', 
        frequency     = '6hr', 
        updated_on  = '20181029',
        fdate  = '19790101',
        tdate  = '20180831')
    var2_1 = insert_unique(db, Variable,
        dataset_id = ds2id,
        name        = 'T',
        long_name   = 'temperature ...',
        standard_name   = 'air_temperature',
        cmor_name  = 'ta',
        units      = 'K',
        levels     = '1000 900 800 500 200 0', 
        grid     = 'NA', 
        frequency     = '6hr', 
        updated_on  = '20181029',
        fdate  = '20000101',
        tdate  = '20180831')
    var2_2 = insert_unique(db, Variable,
        dataset_id = ds2id,
        name        = 'prec',
        long_name   = 'precipitation ...',
        standard_name   = 'rainfall_rate',
        cmor_name  = 'pr',
        units      = 'mm day-1',
        levels     = '1000 900 800 500 200 0', 
        grid     = 'NA', 
        frequency     = '6hr', 
        updated_on  = '20181029',
        fdate  = '20000101',
        tdate  = '20180831')
    db.commit()

    # Close the session
    def fin():
        db.close()
    request.addfinalizer(fin)

    return session

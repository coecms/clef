#!/usr/bin/env python
# This collects all functions to update database using SQLalchemy
"""
Copyright 2018 ARC Centre of Excellence for Climate Systems Science
author: Paola Petrelli <paola.petrelli@utas.edu.au>
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

from __future__ import print_function

from sqlalchemy.orm.exc import NoResultFound
from . import collections as colls  
from .db_noesgf import *


def search_item(db, klass, **kwargs):
    """
    Search for item in DB, if it can't be found return False
    Otherwise returns only first item
    """
    try:
        item = db.query(klass).filter_by(**kwargs).one()
    except NoResultFound:
        return False
    return item

def insert_unique(db, klass, **kwargs):
    """
    Insert an item into the DB if it can't be found
    NB need to commit before terminating session
    Returns id, True if new item, id False if existing
    """
    item = search_item(db, klass, **kwargs)
    new=False
    if not item:
        item = klass(**kwargs)
        db.add(item)
        new=True
        db.commit() 

def add_bulk_items(db, klass, rows):
    """Batched INSERT statements via the ORM "bulk", using dictionaries.
       input: rows is a list of dictionaries """
    db.bulk_insert_mappings(klass,rows) 
    db.commit()
    return

def update_item(db, klass, item_id, newvalues):
    '''Update database item 
       :argument: db database SQLalchemy connection session 
       :argument: klass class representing table objects
       :argument: item_id the id for row to update
       :argument: newvalues a dictionary with the column keys, values to be updated
       :return nothing
    '''
    db.query(klass).filter_by(id=item_id).update(newvalues)
    db.commit()
    return

def commit_changes(db):
    ''' Commit changes to database '''
    return db.commit()


def add_dataset(name, version, fformat, **kwargs):
    '''
    Add dataset to clef catalog of not-ESGF datasets
    :input: name dataset name 
    :input: version
    :input: fformat
    :kwargs: other fields (optional): 
    '''
    # open connection to database
    db = colls.connect()
    clefdb = db.session
    # first check if dataset as defined by (name, version, format) already exists
    ds = clefdb.query(Dataset.name==name).all()
    if len(ds) > 0:
        for d in ds:
            if d.fileformat == fformat and d.version == version:
                print(f'Dataset $name v$version ($fformat) exists already.\n Aborting operation')
                return 
    else:
            kwargs['name'] = name
            kwargs['fileformat'] = fformat 
            kwargs['version'] = version
            insert_unique(clefdb, Dataset, **kwargs)
            print(f'Dataset $name v$version ($fformat) added to collection.')
            return 


def add_ecmwf_table(table):
    ''' 
    Add an ECMWF table as a bulk transaction
    :input: table a list of dictionaries representing the table 
    '''
    # open connection to database
    db = colls.connect()
    clefdb = db.session
    # check that table is a list of dictionaries with the right keys
    keys = ['code', 'name', 'cds_name', 'units', 'long_name', 'standard_name', 'cmor_name', 'cell_methods']
    table_keys = list(table[0].keys())  
    assert sorted(keys) == sorted(table_keys)
    # add bulk
    add_bulk_items(clefdb, ECMWF, table)
    return


def add_variable_table(rows,dname,fformat,version):
    ''' 
    Add an Variable table as a bulk transaction
    :input: rows a list of dictionaries representing the table rows 
    '''
    # open connection to database
    db = colls.connect()
    clefdb = db.session
    # find the dataset_id
    dsid = clefdb.query(Dataset.id).filter_by(**{'name': dname, 'fileformat': fformat, 'version': version}).one_or_none()
    assert dsid 
    # add dataset_id to all the rows
    for row in rows:
        row['dataset_id'] = dsid[0] 
    # find missing information for each parameter code from ECMWF table
    #if dname in ['ERAI', 'MACC', 'ERA5', 'YOTC']:
    if dname in [ 'MACC', 'ERA5', 'YOTC']:
        for row in rows:
            code = row.pop('code')
            vals = clefdb.query(ECMWF).filter(ECMWF.code == code).one_or_none()
            if vals:
                row['name'] = vals.name
                row['standard_name'] = vals.standard_name
                row['long_name'] = vals.long_name
                row['cmor_name'] = vals.cmor_name
                row['units'] = vals.units
            else:
                print(f'Warning: unrecognised code {code} in ECMWF table, this variable will be added with incomplete information')
    # check that table is a list of dictionaries with the right keys
    keys = ['dataset_id', 'name', 'long_name', 'standard_name', 'cmor_name', 'units', 'levels', 'grid', 'resolution', 'frequency', 'fdate', 'tdate','stream','realm']
    rows_keys = list(rows[0].keys())  
    assert sorted(keys) == sorted(rows_keys)
        
    # add bulk
    add_bulk_items(clefdb, Variable, rows)
    return

def update_variable_table(rows,identifiers,dname,fformat,version):
    ''' 
    Update Variable table 
    :input: rows a list of dictionaries representing the table rows 
    :input: dname dataset name as in Dataset table
    '''
    # open connection to database
    db = colls.connect()
    clefdb = db.session
    # find the dataset_id
    dsid = clefdb.query(Dataset.id).filter_by(**{'name': dname, 'fileformat': fformat, 'version': version}).one_or_none()
    assert dsid 
    # add dataset_id to arguments to search 
    # transfer row dict item which are identifiers to kwargs dict
    for row in rows:
        kwargs={}
        kwargs['dataset_id'] = dsid[0] 
        for key in identifiers:
            kwargs[key] = row.pop(key)
        # search row in db and update
        vid = clefdb.query(Variable).filter_by(**kwargs).one_or_none()
        if vid:
           row['id'] = vid
           update_item(clefdb, Variable, row)
        else:
           print(f'Warning could not find a variable with constraints:\n   {kwargs}')
    return

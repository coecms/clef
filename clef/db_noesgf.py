#!/usr/bin/env python
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

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
#from clef.data import *

import os
import re

Base = declarative_base()

class Dataset(Base):
    """
    Each record define main characteristics of one dataset.
    A dataset must have only one file format, version, drs and filename structure. If ore then one exists for the same data then these are two separate datasets with same name. 
    Search through these using :func:`
    .. attribute:: name 
        Dataset name
    .. attribute:: version 
        Dataset version
    .. attribute:: drs 
        Directory structure pattern
    .. attribute:: filename 
        Filename pattern
    .. attribute:: fileformat 
        File format
    .. attribute:: access 
        Access rules: i.e. NCI group membership and/or creators terms
    .. attribute:: manager 
        Dataset manager e-mail
    .. attribute:: reference 
        A url referencing infomration on the dataset
    """
    __tablename__ = 'datasets'
    id         = Column(Integer, name='dataset_id', primary_key = True)
    name       = Column(String, index=True)
    version    = Column(String, index=True)
    drs        = Column(String)
    filename   = Column(String)
    fileformat = Column(String, name='format', index=True)
    access     = Column(String)
    manager    = Column(String)
    reference  = Column(String)

    variables  = relationship('Variable', backref='dataset', order_by='Variable.varname', 
                 cascade="all, delete-orphan", passive_deletes=True)

    __table_args__ = (
            UniqueConstraint('name','format','version'),
            )


class Variable(Base):
    """
    Each record represents a variable for a specific dataset. 
    i.e. you can have T defined for ERAI and for ERA5 and they will be two seperate records even if all attributes might be the same  
    .. attribute:: id 
        :class:`Dataset` associated with this record (foreign key)
    .. attribute:: varname 
        Variable name as defined in the file (for self-describing formats)
    .. attribute:: long_name 
        long_name attribute definition 
    .. attribute:: standard_name 
        standard_name attribute definition 
    .. attribute:: cmor_name 
        corresponding cmor_name if exists 
    .. attribute:: units
        Variable units 
    .. attribute:: grid 
        Label for grid on which variable is defined (or actual boundary?)
    .. attribute:: resolution 
       Grid resolution
    .. attribute:: stream 
       Group/subset to which variable belongs to where it applies, i.e. for ECMWF datasets 
    .. attribute:: realm 
       variable realm: ie. atmos, ocean etc where it applies, i.e. for all datasets following CMOR conventions
    .. attribute:: frequency 
       Frequency as: mon, 6hr, yr, ...
    .. attribute:: levels 
       Vertical levels: a list of values, empty (or 0??) if surface field
    #.. testsetup::
    #    >>> cmip5  = getfixture('session')
    """
    __tablename__ = 'variables'
    id          = Column(Integer, name='variable_id', primary_key = True)
    dataset_id  = Column(Integer, ForeignKey('datasets.dataset_id'), index=True)

    varname           = Column(String)
    long_name      = Column(String)
    standard_name  = Column(String, index=True)
    cmor_name      = Column(String, index=True)
    units          = Column(String)
    grid           = Column(String)
    resolution     = Column(String)
    stream         = Column(String)
    realm          = Column(String)
    frequency      = Column(String, index=True)
    levels         = Column(String)
    fdate          = Column(String)
    tdate          = Column(String)
    updated_on     = Column(String)

    def path(self):
        """
        Returns the filepath pattern for a variable based on the drs and filename pattern 
        :returns: 
        """
        drs = self.dataset.drs + self.dataset.filename 
        placeholds = re.findall('<[a-zA-Z]*[_]?[a-zA-Z]*>', drs)
        for col in Dataset.__table__.columns.keys():
            if "<"+col+">" in placeholds:
                drs = drs.replace("<"+col+">",getattr(self.dataset,col))
        for col in Variable.__table__.columns.keys():
            if "<"+col+">" in placeholds and 'date' not in col:
                drs = drs.replace("<"+col+">",getattr(self,col))
        return drs 


class ECMWF(Base):
    """
    Each record represents a variable for a specific dataset. 
    i.e. you can have T defined for ERAI and for ERA5 and they will be two seperate records even if all attributes might be the same  
    .. attribute:: id 
    .. attribute:: code 
        Grib code for variable: <code>.<table>
    .. attribute:: name 
        Variable name used in ECMWF files
    .. attribute:: cds_name 
        Variable name used for requests via Copernicus climate service
    .. attribute:: units
        Variable units 
    .. attribute:: long_name 
        long_name attribute definition 
    .. attribute:: standard_name 
        standard_name attribute definition 
    .. attribute:: cmor_name 
        corresponding cmor_name if exists 
    .. attribute:: cell_methods 
       Cell_methods attribute for variable if applicable
    """
    __tablename__ = 'ecmwf_vars'
    id          = Column(Integer, name='ecmwf_var_id', primary_key = True)

    code           = Column(String)
    name           = Column(String)
    cds_name      = Column(String)
    units          = Column(String)
    long_name      = Column(String)
    standard_name  = Column(String, index=True)
    cmor_name      = Column(String, index=True)
    cell_methods   = Column(String)


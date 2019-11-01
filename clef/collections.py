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

import os

from sqlalchemy import create_engine, func, select, and_, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects import sqlite

from .db_noesgf import Base, Dataset, Variable, ECMWF, QC

SQASession = sessionmaker()

class Session(object):
    """Holds a connection to the catalog
    Create using :func:`clef.dataset.connect()`
    """

    def query(self, *args, **kwargs):
        """Query the not-ESGF collections catalog
        Allows you to filter the full list of datasets using `SQLAlchemy commands <http://docs.sqlalchemy.org/en/rel_1_0/orm/tutorial.html#querying>`_
        :return: A SQLalchemy query object
        """
        return self.session.query(*args, **kwargs)

    def files(self, **kwargs):
        """ Query the list of files
        Returns a list of files that match the arguments
        :argument **kwargs: Match any attribute in :class:`Model.Instance`, e.g. `model = 'ACCESS1-3'`
        :return: An iterable returning :py:class:`Model.File`
            matching the search query
        """
        raise NotImplementedError

    def dsets(self):
        """ Get the list of all the datasets including version number and the file format
        :return: A list of strings
        """
        sets = self.query(Dataset).all()
        return [x.name + " v"+ x.version + " (" + x.fileformat + ")" for x in sets]

    def standard_names(self):
        """ Get the list of all variables in datasets collection as standard_names
        :return: A list of strings
        """
        return [x[0] for x in self.query(Variable.standard_name).distinct().all()]

    def vars_names(self):
        """ Get the list of all variables in datasets collection as actual names
        :return: A list of strings
        """
        return [x[0] for x in self.query(Variable.varname).distinct().all()]

    def cmor_names(self):
        """ Get the list of all variables in datasets collection as cmor names
        :return: A list of strings
        """
        return [x[0] for x in self.query(Variable.cmor_name).distinct().all()]

    def qc_list(self, dataset=None):
        """ Get the list of all the qc tests in qc table, if dataset passed only the one applying to it
        :input: dataset optional if passed return only tests for that dataset
        :return: A list of strings
        """
        if dataset:
            #return [x[0] for x in self.query(QC.qc_test).where(QC.dataset=dataset).distinct().all()]
            pass
        return [x[0] for x in self.query(QC.qc_test).distinct().all()]

    def command_query(self,**kwargs):
        """ Calling query after working out if output should be a dataset or variable list, depending on constraints
            passed by the user.
           :input: 
           :return:
        """
        # empty dictionaries to separate constraints for dataset and variable tables
        dsargs={}
        vargs={}
        vlargs={}
        variables = []
        if kwargs['dname']: dsargs['name'] = kwargs.pop('dname')
        if kwargs['version']: dsargs['version'] = kwargs.pop('version')
        if kwargs['fileformat']: dsargs['fileformat'] = kwargs.pop('fileformat')
        ds_outs = self.query(Dataset).filter_by(**dsargs).all()
        if ds_outs:
            kwargs['dataset_id'] = [ds.id for ds in ds_outs]
            datasets = [x for x in ds_outs]
        for k,v in kwargs.items():
            if v not in [None, ()]:
                if len(v) > 1:
                    vlargs[k] = [x for x in v]
                else:
                    vargs[k] = v[0] 
        # if dataset_id is the only key in vargs, return datasets only
        if len(vargs.keys()) + len(vlargs.keys()) == 1:
            return datasets, variables, False 
        # build query filtering all single value arguments: vargs
        # filter query results using in_() for list of values arguments: vlargs
        q1 = self.query(Variable).filter_by(**vargs) 
        for attr, value in vlargs.items():
            q = q1.filter(getattr(Variable, attr).in_(value))
        #print( str(q.statement.compile(dialect=sqlite.dialect())))
        var_outs = q.all()
        if var_outs:
            variables= [x for x in var_outs]
        return datasets, variables, True

# Default collections database
default_db = 'sqlite:////g/data1/ua8/Download/clef.db'

def connect(path = None):
    """Connect to the not-ESGF datasets catalog
    :return: A new :py:class:`Session`
    Example::
    >>> from clef import collections
    >>> clefdb   = collections.connect() # doctest: +SKIP
    >>> outputs = clefdb.query() # doctest: +SKIP
    """

    if path is None:
        # Get the path from the environment
        path = os.environ.get('CLEF_DB', default_db)

    engine = create_engine(path)
    Base.metadata.create_all(engine)
    SQASession.configure(bind=engine, autoflush=False)

    connection = Session()
    connection.session = SQASession()
    return connection

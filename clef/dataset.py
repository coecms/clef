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

from __future__ import print_function

import os

from sqlalchemy import create_engine, func, select, and_
from sqlalchemy.orm import sessionmaker

from clef.db_noesgf import Base, Dataset, Variable

SQASession = sessionmaker()

class Session(object):
    """Holds a connection to the catalog
    Create using :func:`clef.dataset.connect()`
    """

    def query(self, *args, **kwargs):
        """Query the non-ESGF collections catalog
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

    def variables(self):
        """ Get the list of all variables in datasets collection as standard_names
        :return: A list of strings
        """
        return [x[0] for x in self.query(Variable.standard_name).distinct().all()]

# Default collections database
default_db = 'sqlite:////g/data1/ua8/Download/datadb.db'

def connect(path = None):
    """Connect to the not-ESGF datasets catalog
    :return: A new :py:class:`Session`
    Example::
    >>> from clef import dataset 
    >>> clefdb   = dataset.connect() # doctest: +SKIP
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

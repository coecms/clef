#!/usr/bin/env python
# Copyright 2019 ARC Centre of Excellence for Climate Extremes
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
from __future__ import print_function

from clef.code import local_query
import clef.db
import pytest
import os
import sqlalchemy as sa

raijin_only = pytest.mark.skipif(not os.environ.get('HOSTNAME', '').startswith('raijin'),
        reason="Test only available on Raijin")


@pytest.fixture(scope='session')
def prod_session():
    # Session connected to the production db
    url = clef.db.default_url
    engine = sa.create_engine(url)
    Session = sa.orm.sessionmaker(bind=engine)

    # Ensure read-only
    @sa.event.listens_for(Session, 'before_flush')
    def recv_before_flush(*args,**kwargs):
        raise Exception("Read only session!")

    session = Session()
    yield session
    session.rollback()


#@raijin_only
def test_local_access1_model(session):
    # Check we have ACCESS model results
    q = local_query(session, project='cmip5',
            model='ACCESS1.0',
            experiment='historical',
            ensemble='r1i1p1',
            cmor_table='Amon',
            variable='tas',
            )
    assert len(q) > 0


#@raijin_only
def test_local_hadgem_model(session):
    # Check we have HadGEM model results
    q = local_query(session, project='cmip5',
            model='HadGEM2-AO',
            experiment='historical',
            ensemble='r1i1p1',
            cmor_table='Amon',
            variable='tas',
            )
    assert len(q) > 0

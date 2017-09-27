#!/usr/bin/env python
# Copyright 2017 ARC Centre of Excellence for Climate Systems Science
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

"""
Model of NCI's MAS database
"""

from __future__ import print_function

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.indexable import index_property
from sqlalchemy import Column, ForeignKey, Text, Integer, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

Base = declarative_base()

class pg_json_property(index_property):
    # http://docs.sqlalchemy.org/en/latest/orm/extensions/indexable.html
    def __init__(self, attr_name, index, cast_type):
        super(pg_json_property, self).__init__(attr_name, index)
        self.cast_type = cast_type

    def expr(self, model):
        expr = super(pg_json_property, self).expr(model)
        return expr.astext.cast(self.cast_type)

metadata_dataset_link = Table('esgf_metadata_dataset_link', Base.metadata,
    Column('file_id', 
        ForeignKey('paths.pa_hash'), 
        ForeignKey('metadata.md_hash'),
        ForeignKey('checksums.ch_hash')),
    Column('dataset_id', ForeignKey('esgf_dataset.dataset_id')))

class Path(Base):
    __tablename__ = 'paths'

    id = Column('pa_hash', UUID, primary_key=True)
    path = Column('pa_path', Text)

class Metadata(Base):
    __tablename__ = 'metadata'

    id = Column('md_hash', UUID, ForeignKey('paths.pa_hash'), primary_key=True)
    type = Column('md_type', Text, primary_key=True)
    json = Column('md_json', JSONB)

    path = relationship("Path")

    __mapper_args__ = {
            'polymorphic_on': type,
            }

class Checksum(Base):
    __tablename__ = 'checksums'

    id = Column('ch_hash', UUID, ForeignKey('paths.pa_hash'), ForeignKey('metadata.md_hash'), primary_key=True)
    md5 = Column('ch_md5', String)
    sha256 = Column('ch_sha256', String)

    path = relationship("Path")

class Posix(Metadata):
    __mapper_args__ = {
            'polymorphic_identity': 'posix',
            }

class Netcdf(Metadata):
    __mapper_args__ = {
            'polymorphic_identity': 'netcdf',
            }

    format     = pg_json_property('json', 'format', Text)
    variables  = index_property('json', 'variables')
    attributes = index_property('json', 'attributes')
    dimensions = index_property('json', 'dimensions')

    frequency             = pg_json_property('attributes', 'frequency', Text)
    modeling_realm        = pg_json_property('attributes', 'modeling_realm', Text)
    parent_experiment_id  = pg_json_property('attributes', 'parent_experiment_id', Text)
    parent_experiment_rip = pg_json_property('attributes', 'parent_experiment_rip', Text)
    realization           = pg_json_property('attributes', 'realization', Integer)
    experiment_id         = pg_json_property('attributes', 'experiment_id', Text)
    experiment            = pg_json_property('attributes', 'experiment', Text)
    creation_date         = pg_json_property('attributes', 'creation_date', Text)
    forcing               = pg_json_property('attributes', 'forcing', Text)
    institute_id          = pg_json_property('attributes', 'institute_id', Text)
    source                = pg_json_property('attributes', 'source', Text)
    title                 = pg_json_property('attributes', 'title', Text)
    physics_version       = pg_json_property('attributes', 'physics_version', Integer)
    project_id            = pg_json_property('attributes', 'project_id', Text)
    institution           = pg_json_property('attributes', 'institution', Text)
    version_number        = pg_json_property('attributes', 'version_number', Text)
    initialization_method = pg_json_property('attributes', 'initialization_method', Integer)
    table_id              = pg_json_property('attributes', 'table_id', Text)
    branch_time           = pg_json_property('attributes', 'branch_time', Text)
    Conventions           = pg_json_property('attributes', 'Conventions', Text)
    tracking_id           = pg_json_property('attributes', 'tracking_id', Text)
    parent_experiment     = pg_json_property('attributes', 'parent_experiment', Text)
    product               = pg_json_property('attributes', 'product', Text)
    model_id              = pg_json_property('attributes', 'model_id', Text)

class Dataset(Base):
    __tablename__ = 'esgf_dataset'

    dataset_id = Column(Text, primary_key=True)
    institute = Column(Text)
    model = Column(Text)
    experiment = Column(Text)
    frequency = Column(Text)
    realm = Column(Text)
    r = Column(Integer)
    i = Column(Integer)
    p = Column(Integer)
    ensemble = Column(Text)

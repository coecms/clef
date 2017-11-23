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
from sqlalchemy.dialects.postgresql import UUID, JSONB, INT4RANGE

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
        ForeignKey('esgf_paths.file_id'), 
        ForeignKey('metadata.md_hash'),
        ForeignKey('checksums.ch_hash')),
    Column('dataset_id', ForeignKey('esgf_dataset.dataset_id')))

class Path(Base):
    __tablename__ = 'esgf_paths'

    id = Column('file_id', UUID, primary_key=True)
    path = Column('path', Text)

    dataset = relationship('Dataset', secondary=metadata_dataset_link, viewonly=True)
    netcdf = relationship('Netcdf', viewonly=True)
    checksum = relationship('Checksum', viewonly=True)
    extended = relationship('ExtendedMetadata', viewonly=True)

class Metadata(Base):
    __tablename__ = 'metadata'

    id = Column('md_hash', UUID, ForeignKey('esgf_paths.file_id'), primary_key=True)
    type = Column('md_type', Text, primary_key=True)
    json = Column('md_json', JSONB)

    path = relationship("Path")

    __mapper_args__ = {
            'polymorphic_on': type,
            }

class Checksum(Base):
    __tablename__ = 'checksums'

    id = Column('ch_hash', UUID, ForeignKey('esgf_paths.file_id'), ForeignKey('metadata.md_hash'), primary_key=True)
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

class ExtendedMetadata(Base):
    """
    Extra metadata not present in the file's attributes
    """
    __tablename__ = 'extended_metadata'

    file_id = Column(UUID,
            ForeignKey('metadata.md_hash'),
            ForeignKey('checksums.ch_hash'),
            ForeignKey('esgf_paths.file_id'),
            primary_key=True)
    version = Column(Text)
    variable = Column(Text)
    period = Column(INT4RANGE)

class Dataset(Base):
    """
    An ESGF dataset
    """
    __tablename__ = 'esgf_dataset'

    dataset_id = Column(Text, primary_key=True)
    project = Column(Text)
    institute = Column(Text)
    model = Column(Text)
    experiment = Column(Text)
    time_frequency = Column('frequency', Text)
    realm = Column(Text)
    r = Column(Integer)
    i = Column(Integer)
    p = Column(Integer)
    ensemble = Column(Text)
    cmor_table = Column(Text)

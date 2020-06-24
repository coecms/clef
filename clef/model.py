#!/usr/bin/env python
# Copyright 2017 ARC Centre of Excellence for Climate Extremes 
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
Model of NCI's clef.nci.org.au database

The database has two main tables - ``path`` and ``metadata``. These base
tables are available in the model as :class:`Path` and :class:`Metadata`, they
have a SQLAlchemy relationship so that the two table can be joined in queries.

There may be multiple :class:`Metadata` entries for a single :class:`Path`,
these represent different metadata types, such as checksums, netCDF attributes
and POSIX file attributes. The type can be identified from
:attr:`Metadata.type`, and is used as a polymorphic identity to SQLAlchemy's
`single table inheritance <https://docs.sqlalchemy.org/en/latest/orm/inheritance.html#relationships-with-single-table-inheritance>`_,
creating the :class:`Checksum`, :class:`Netcdf` and :class:`Posix` models.

The :class:`C5Dataset` and :class:`C6Dataset` models represent datasets like
you would find on ESGF, although without a version. They are created in the
database from a ``DISTINCT`` view of the NetCDF attributes, and can be used to
group paths on the filesystem into datasets.
"""


from sqlalchemy import Column, ForeignKey, Text, Integer, String, Table
from sqlalchemy.dialects.postgresql import UUID, JSONB, INT4RANGE
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.indexable import index_property
from sqlalchemy.orm import relationship


Base = declarative_base()


class pg_json_property(index_property):
    # http://docs.sqlalchemy.org/en/latest/orm/extensions/indexable.html
    def __init__(self, attr_name, index, cast_type):
        super(pg_json_property, self).__init__(attr_name, index)
        self.cast_type = cast_type

    def expr(self, model):
        expr = super(pg_json_property, self).expr(model)
        return expr.astext.cast(self.cast_type)


# These tables group the individual files into datasets. `dataset_id` is essentially a md5 checksum of the ESGF
# dataset id, generated from the netcdf attributes
c5_metadata_dataset_link = Table('c5_metadata_dataset_link', Base.metadata,
                                 Column('file_id',
                                        ForeignKey('esgf_paths.file_id'),
                                        ForeignKey('metadata.md_hash'),
                                        ForeignKey('checksums.ch_hash')),
                                 Column('dataset_id', ForeignKey('cmip5_dataset.dataset_id')))

c6_metadata_dataset_link = Table('c6_metadata_dataset_link', Base.metadata,
                                 Column('file_id',
                                        ForeignKey('esgf_paths.file_id'),
                                        ForeignKey('metadata.md_hash'),
                                        ForeignKey('checksums.ch_hash')),
                                 Column('dataset_id', ForeignKey('cmip6_dataset.dataset_id')))


class Path(Base):
    """Path of a file on Raijin, with links to metadata
    """
    __tablename__ = 'esgf_paths'

    id = Column('file_id', UUID, primary_key=True)

    #: File path at NCI
    path = Column('path', Text)

    #: :class:`C5Dataset`:
    c5dataset = relationship('C5Dataset', secondary=c5_metadata_dataset_link, viewonly=True)

    #: :class:`C6Dataset`:
    c6dataset = relationship('C6Dataset', secondary=c6_metadata_dataset_link, viewonly=True)

    #: :class:`Netcdf`:
    netcdf = relationship('Netcdf', viewonly=True)

    #: :class:`Checksum`:
    checksum = relationship('Checksum', viewonly=True)

    extended = relationship('ExtendedMetadata', viewonly=True)


class Metadata(Base):
    """Generic base class for Metadata of a file on Raijin

    See :class:`Posix` and :class:`Netcdf` for specific metadata information
    """
    __tablename__ = 'metadata'

    id = Column('md_hash', UUID, ForeignKey('esgf_paths.file_id'), primary_key=True)

    #: Metadata type
    type = Column('md_type', Text, primary_key=True)

    #: Metadata value
    json = Column('md_json', JSONB)

    #: :class:`Path`:
    path = relationship("Path")

    __mapper_args__ = {
        'polymorphic_on': type,
    }


class Checksum(Base):
    """Checksum of a file on Raijin
    """
    __tablename__ = 'checksums'

    id = Column('ch_hash', UUID, ForeignKey('esgf_paths.file_id'), ForeignKey('metadata.md_hash'), primary_key=True)

    #: md5 checksum
    md5 = Column('ch_md5', String)

    #: sha256 checksum
    sha256 = Column('ch_sha256', String)

    #: :class:`Path`:
    path = relationship("Path")


class Posix(Metadata):
    """Posix metadata of a file on Raijin

    As would be found by ``ls``
    """
    __mapper_args__ = {
        'polymorphic_identity': 'posix',
    }


class Netcdf(Metadata):
    """NetCDF metadata of a file on Raijin

    As would be found by ``ncdump -h``
    """
    __mapper_args__ = {
        'polymorphic_identity': 'netcdf',
    }

    format = pg_json_property('json', 'format', Text)

    #: File variables
    variables = index_property('json', 'variables')

    #: File attributes
    attributes = index_property('json', 'attributes')

    #: File dimensions
    dimensions = index_property('json', 'dimensions')


class ExtendedMetadata(Base):
    """Extra metadata not present in the file's attributes
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


class C5Dataset(Base):
    """A CMIP5-era ESGF dataset

    This class only has access to attributes from the file itself, so version
    information is not present.

    See the CMIP documentation for descriptions of the attributes
    """
    __tablename__ = 'cmip5_dataset'

    dataset_id = Column(Text, primary_key=True)

    #:
    project = Column(Text)

    #:
    institute = Column(Text)

    #:
    model = Column(Text)

    #:
    experiment = Column(Text)

    #:
    time_frequency = Column('frequency', Text)

    #:
    realm = Column(Text)

    r = Column(Integer)
    i = Column(Integer)
    p = Column(Integer)

    #:
    ensemble = Column(Text)

    #:
    cmor_table = Column(Text)


class C6Dataset(Base):
    """A CMIP6-era ESGF dataset

    This class only has access to attributes from the file itself, so version
    information is not present.

    See the CMIP documentation for descriptions of the attributes
    """
    __tablename__ = 'cmip6_dataset'

    dataset_id = Column(Text, primary_key=True)

    #:
    project = Column(Text)

    #:
    activity_id = Column('activity_id', Text)

    #:
    institution_id = Column('institution_id', Text)

    #:
    source_id = Column('source_id', Text)

    #:
    source_type = Column('source_type', Text)

    #:
    experiment_id = Column('experiment_id', Text)

    #:
    sub_experiment_id = Column('sub_experiment_id', Text)

    #:
    frequency = Column('frequency', Text)

    #:
    realm = Column(Text)

    r = Column(Integer)
    i = Column(Integer)
    p = Column(Integer)
    f = Column(Integer)

    #:
    variant_label = Column('variant_label', Text)

    #:
    member_id = Column('member_id', Text)

    #:
    variable_id = Column(Text)

    #:
    grid_label = Column('grid_label', Text)

    #:
    nominal_resolution = Column('nominal_resolution', Text)

    #:
    table_id = Column('table_id', Text)


class Info(Base):
    """
    General information about a dataset file

    This is a database view, its columns shouldn't be used for searching as
    they are large and not indexed.
    """
    __tablename__ = 'info_attributes'

    file_id = Column(UUID,
                     ForeignKey('metadata.md_hash'),
                     ForeignKey('checksums.ch_hash'),
                     ForeignKey('esgf_paths.file_id'),
                     primary_key=True)

    #:
    variant_info = Column(Text)
    #:
    source = Column(Text)
    #:
    parent_experiment_id = Column(Text)
    #:
    further_info_url = Column(Text)
    #:
    contact = Column(Text)
    #:
    title = Column(Text)
    #:
    description = Column(Text)
    #:
    license = Column(Text)
    #:
    tracking_id = Column(Text)

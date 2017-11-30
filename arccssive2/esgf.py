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
from __future__ import print_function
import requests
from sqlalchemy.sql import column, label
from sqlalchemy.orm import aliased
from sqlalchemy import String, Float, Integer, or_
from .pgvalues import values
from .model import Path, Checksum, metadata_dataset_link

def esgf_query(query, fields, limit=1000, offset=0, distrib=True, replica=False, latest=None,
        cf_standard_name=None,
        ensemble=None,
        experiment=None,
        experiment_family=None,
        institute=None,
        cmor_table=None,
        model=None,
        project=None,
        product=None,
        realm=None,
        time_frequency=None,
        variable=None,
        variable_long_name=None,
        source_id=None,
        ):
    """
    Search the ESGF
    """
    if latest == 'all':
        latest = None

    if query is not None and len(query) == 0:
        query = None

    r = requests.get('https://esgf.nci.org.au/esg-search/search',
            params = {
                'query': query,
                'fields': fields,
                'offset': offset,
                'limit': limit,
                'distrib': distrib,
                'replica': replica,
                'latest': latest,
                'cf_standard_name':cf_standard_name,
                'ensemble':ensemble,
                'experiment':experiment,
                'experiment_family':experiment_family,
                'institute':institute,
                'cmor_table':cmor_table,
                'model':model,
                'project':project,
                'product':product,
                'realm':realm,
                'time_frequency':time_frequency,
                'variable':variable,
                'variable_long_name':variable_long_name,
                'source_id':source_id,
                'type': 'File',
                'format': 'application/solr+json',
                })

    r.raise_for_status()

    return r.json()

def link_to_esgf(query, **kwargs):
    r = requests.Request('GET','https://esgf.nci.org.au/search/esgf_nci',
            params = {
            'query': query,
            'fields': kwargs.get('fields',None),
            'offset': kwargs.get('offset',None),
            'limit': kwargs.get('limit',None),
            'distrib': 'on' if kwargs.get('distrib',True) else None,
            'replica': 'on' if kwargs.get('replica',False) else None,
            'latest': 'on' if kwargs.get('latest',None) else None,
            'cf_standard_name': kwargs.get('cf_standard_name',None),
            'ensemble': kwargs.get('ensemble',None),
            'experiment': kwargs.get('experiment',None),
            'experiment_family': kwargs.get('experiment_family',None),
            'institute': kwargs.get('institute',None),
            'cmor_table': kwargs.get('cmor_table',None),
            'model': kwargs.get('model',None),
            'project': kwargs.get('project',None),
            'product': kwargs.get('product',None),
            'realm': kwargs.get('realm',None),
            'time_frequency': kwargs.get('time_frequency',None),
            'variable': kwargs.get('variable',None),
            'variable_long_name': kwargs.get('variable_long_name',None),
            'source_id': kwargs.get('source_id',None),
            })
    return r.prepare().url


def find_checksum_id(query, **kwargs):
    """
    Returns a sqlalchemy selectable containing the ESGF id and checksum for
    each query match
    """
    response = esgf_query(query, 'checksum,id,tracking_id,version', **kwargs)

    if response['response']['numFound'] == 0:
        raise Exception('No matches found on ESGF, check at %s'%link_to_esgf(query, **kwargs))

    if response['response']['numFound'] > int(response['responseHeader']['params']['rows']):
        raise Exception('Too many results (%d), try limiting your search %s'%(response['response']['numFound'], link_to_esgf(query, **kwargs)))

    table = values([
            column('checksum', String),
            column('id', String),
            column('tracking_id', String),
            column('version', Integer),
            column('score', Float),
        ],
        *[(
            doc['checksum'][0],
            doc['id'],
            doc['tracking_id'][0],
            doc['version'],
            doc['score'])
            for doc in response['response']['docs']],
        alias_name = 'esgf'
        )

    return table

def find_local_path(session, query, **kwargs):
    """
    Returns the `model.Path` for each local file found in the ESGF query
    
    If the file exists but at a different version return that as well

    SELECT DISTINCT ON (tracking_id) path FROM paths
    NATURAL JOIN metadata_dataset_link
    JOIN query ON (tracking_id)
    ORDER BY tracking_id, version DESC, path
    """
    values = find_checksum_id(query, **kwargs)
    
    return (session.query(Path)
            .join(Checksum)
            .join(metadata_dataset_link)
            .join(values, 
                or_(Checksum.md5 == values.c.checksum, 
                    Checksum.sha256 == values.c.checksum))
            .order_by(values.c.score))

def find_missing_id(session, query, **kwargs):
    """
    Returns the ESGF id for each file in the ESGF query that doesn't have a
    local match
    """
    values = find_checksum_id(query, **kwargs)

    subq = session.query(Checksum).join(metadata_dataset_link).subquery()
    filtered_sum = aliased(Checksum, subq)
    
    return (session.query('id')
            .select_from(
                values.outerjoin(filtered_sum, 
                    or_(filtered_sum.md5 == values.c.checksum, 
                        filtered_sum.sha256 == values.c.checksum)))
            .filter(filtered_sum.id == None)
            .order_by(values.c.score))


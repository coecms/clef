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
import json
from sqlalchemy.sql import column, label
from sqlalchemy.orm import aliased
from sqlalchemy import String, Float, Integer, or_, func
from .pgvalues import values
from .model import Path, Checksum, c5_metadata_dataset_link, c6_metadata_dataset_link

def define_facets(project):
    ''' Define available search facets based on project value: CMIP5 or CMIP6 '''
    with open('../db/facets.json', 'r') as f: 
       data = f.read()
       fdict = json.loads(data)
    if project == 'CMIP5':
       facets = {v: None for v in fdict.values() if v != 'None'}
       facets['project'] = 'CMIP5'
    elif project == 'CMIP6': 
       #facets = list(fdict.keys())
       facets = {k: None for k in fdict.keys()}
       facets['project'] = 'CMIP6'
    return facets

def esgf_query(query, fields, limit=1000, offset=0, distrib=True, replica=False, latest=None, **kwargs):
    """
    Search the ESGF
    """
    #facets = define_facets(project)
    if latest == 'all':
        latest = None

    if query is not None and len(query) == 0:
        query = None

    params = {
          'query': query,
          'fields': fields,
          'offset': offset,
          'limit': limit,
          'distrib': distrib,
          'replica': replica,
          'latest': latest, 
          'type': 'File',
          'format': 'application/solr+json',
          } 
    params.update(kwargs)
    r = requests.get('https://esgf-node.llnl.gov/esg-search/search',
                     params = params )

    r.raise_for_status()

    return r.json()

def link_to_esgf(query, **kwargs):
    
    constraints = {k: v for k,v in kwargs.items() if v != ()}
    params = {
            'query': query,
            'fields': kwargs.get('fields',None),
            'offset': kwargs.get('offset',None),
            'limit': kwargs.get('limit',None),
            'distrib': 'on' if kwargs.get('distrib',True) else None,
            'replica': 'on' if kwargs.get('replica',False) else None,
            'latest': 'on' if kwargs.get('latest',None) else None
            }
    params.update(constraints)

    endpoint = 'cmip5'
    if params['project'].lower() == 'cmip6':
        endpoint = 'cmip6'

    r = requests.Request('GET','https://esgf-node.llnl.gov/search/%s'%endpoint,
            params=params,
            )
    p = r.prepare()
    return r.prepare().url


def find_checksum_id(query, project, **kwargs):
    """
    Returns a sqlalchemy selectable containing the ESGF id and checksum for
    each query match
    """
    constraints = {k: v for k,v in kwargs.items() if v != ()}
    constraints['project'] = project
    response = esgf_query(query, 'checksum,id,dataset_id,title,version', **constraints)

    if response['response']['numFound'] == 0:
        raise Exception('No matches found on ESGF, check at %s'%link_to_esgf(query, **constraints))

    if response['response']['numFound'] > int(response['responseHeader']['params']['rows']):
        raise Exception('Too many results (%d), try limiting your search %s'%(response['response']['numFound'], link_to_esgf(query, **constraints)))

    table = values([
            column('checksum', String),
            column('id', String),
            column('dataset_id', String),
            column('title', String),
            column('version', Integer),
            column('score', Float),
        ],
        *[(
            doc['checksum'][0],
            doc['id'],
            doc['dataset_id'].split('|')[0], # Drop the server name
            doc['title'],
            doc['version'],
            doc['score']) 
            for doc in response['response']['docs']],
        alias_name = 'esgf_query'
        )

    return table

def match_query(session, query, latest=None, **kwargs):
    values = find_checksum_id(query, latest=latest, **kwargs)

    if latest is True:
        # Exact match on checksum
        return (values
                .outerjoin(Checksum,
                    or_(Checksum.md5 == values.c.checksum,
                        Checksum.sha256 == values.c.checksum))
                .outerjoin(Path))
    else:
        # Match on file name
        #return values.outerjoin(Path, Path.path.like('%/'+values.c.title))
        return values.outerjoin(Path, func.regexp_replace(Path.path, '^.*/', '') == values.c.title)

def find_local_path(session, query, latest=None, format='file', **kwargs):
    """
    Returns the `model.Path` for each local file found in the ESGF query
    """

    subq = match_query(session, query, latest, **kwargs)
    if format == 'file':
        return (session
                .query('esgf_paths.path')
                .select_from(subq)
                .filter(subq.c.esgf_paths_file_id != None))
    elif format == 'dataset':
        return (session
                .query(func.regexp_replace(subq.c.esgf_paths_path, '[^//]*$', ''))
                .select_from(subq)
                .filter(subq.c.esgf_paths_file_id != None)
                .distinct())
    else:
        raise NotImplementedError

def find_missing_id(session, query, latest=None, format='file', **kwargs):
    """
    Returns the ESGF id for each file in the ESGF query that doesn't have a
    local match
    """

    subq = match_query(session, query, latest, **kwargs)
    if format == 'file':
        return (session
                .query('esgf_query.id')
                .select_from(subq)
                .filter(subq.c.esgf_paths_file_id == None))
    elif format == 'dataset':
        return (session
                .query('esgf_query.dataset_id')
                .select_from(subq)
                .filter(subq.c.esgf_paths_file_id == None)
                .distinct())
    else:
        raise NotImplementedError


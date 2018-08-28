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

"""Functions joining the ESGF web API to the MAS database

 * :func:`esgf_query` handles accessing the web API, and returns its JSON response as a Python dict
 * :func:`find_local_path` and :func:`find_missing_id` match the ESGF results against the MAS database

"""

from __future__ import print_function

import json

import requests
from sqlalchemy import String, Float, Integer, or_, func
from sqlalchemy.sql import column

from .model import Path, Checksum
from .pgvalues import values


def define_facets(project):
    """Define available search facets based on project value: CMIP5 or CMIP6"""
    with open('../db/facets.json', 'r') as f:
        data = f.read()
        fdict = json.loads(data)
    if project == 'CMIP5':
        facets = {v: None for v in fdict.values() if v != 'None'}
        facets['project'] = 'CMIP5'
    elif project == 'CMIP6':
        facets = {k: None for k in fdict.keys()}
        facets['project'] = 'CMIP6'
    else:
        facets = {}
    return facets


def esgf_query(query, fields, limit=1000, offset=0, distrib=True, replica=False, latest=None, **kwargs):
    """Search the ESGF catalogue

    Args:
        query: Free text query
        fields: Fields to return
        limit: Maximum number of items to return
        offset: Starting offset of the returned items (used for paging)
        distrib: Search all nodes (True), or just this one
        replica: Return all replica files (True) or just the master copy
        latest: Return all versions ('all' or None), only the latest (True), or only older copies (False)
        **kwargs: Passed to the ESGF web API as search terms

    Returns:
        dict of ESGF search result (see ESGF web API documentation)
    """
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
                     params=params)

    r.raise_for_status()

    return r.json()


def link_to_esgf(query, **kwargs):
    """Convert search terms to a ESGF search URL

    Returns a link to the user-facing ESGF web search matching a particular query

    This is helpful for error messages, users can follow the URL to find the matches as ESGF sees them

    Args:
        query: Free text query
        **kwargs: As :func:`esgf_query`

    Returns:
        str URL to the ESGF search website
    """
    constraints = {k: v for k, v in kwargs.items() if v != ()}
    params = {
        'query': query,
        'fields': kwargs.get('fields', None),
        'offset': kwargs.get('offset', None),
        'limit': kwargs.get('limit', None),
        'distrib': 'on' if kwargs.get('distrib', True) else None,
        'replica': 'on' if kwargs.get('replica', False) else None,
        'latest': 'on' if kwargs.get('latest', None) else None
    }
    params.update(constraints)

    endpoint = 'cmip5'
    if params.get('project', '').lower() == 'cmip6':
        endpoint = 'cmip6'

    r = requests.Request('GET', 'https://esgf-node.llnl.gov/search/%s' % endpoint,
                         params=params,
                         )
    return r.prepare().url


def find_checksum_id(query, project='CMIP6', **kwargs):
    """Sqlalchemy selectable containing the ESGF id and checksum for each query match

    Args:
        query: Free text query
        project ('CMIP5' or 'CMIP6'): ESGF project to search
        **kwargs: Passed to :func:`esgf_query()`

    Returns:
        :class:`sqlalchemy.sql.expression.Selectable` with the checksum, id, dataset_id, title and version of
             items found on ESGF
    """
    constraints = {k: v for k, v in kwargs.items() if v != ()}
    constraints['project'] = project
    response = esgf_query(query, 'checksum,id,dataset_id,title,version', **constraints)

    if response['response']['numFound'] == 0:
        raise Exception('No matches found on ESGF, check at %s' % link_to_esgf(query, **constraints))

    if response['response']['numFound'] > int(response['responseHeader']['params']['rows']):
        raise Exception('Too many results (%d), try limiting your search %s' % (
                        response['response']['numFound'],
                        link_to_esgf(query, **constraints)))

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
            doc['dataset_id'].split('|')[0],  # Drop the server name
            doc['title'],
            doc['version'],
            doc['score'])
            for doc in response['response']['docs']],
        alias_name='esgf_query'
    )

    return table


def match_query(query, latest=None, **kwargs):
    """Match checksums found on ESGF against the MAS database

    Args:
        query: Free text query
        latest: Return all values ('all' or None), or only the latest (True)
        **kwargs: Passed to :func:`esgf_query`

    Returns:
        :class:`sqlalchemy.sql.expression.Selectable` with the checksum, id, dataset_id, title and version of
             items found on ESGF joined to the matching :class:`arccssive2.model.Path` on the MAS database
    """
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
        # return values.outerjoin(Path, Path.path.like('%/'+values.c.title))
        return values.outerjoin(Path, func.regexp_replace(Path.path, '^.*/', '') == values.c.title)


def find_local_path(session, query, latest=None, format='file', **kwargs):
    """Returns the filesystem path for each local file found in the ESGF query

    Args:
        session (:class:`arccssive2.db.Session`): Database session
        query: Free text query
        latest: Return all values ('all' or None), or only the latest (True)
        format: Return individual files ('file') or whole datasets ('dataset')
        **kwargs: Passed to :func:`esgf_query`

    Returns:
        :class:`sqlalchemy.orm.query.Query` with the list of matching paths of either files or datasets
    """

    subq = match_query(query, latest, **kwargs)
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
    """Returns the ESGF id for each file in the ESGF query that doesn't have a local match

    Args:
        session (:class:`arccssive2.db.Session`): Database session
        query: Free text query
        latest: Return all values ('all' or None), or only the latest (True)
        format: Return individual files ('file') or whole datasets ('dataset')
        **kwargs: Passed to :func:`esgf_query`

    Returns:
        :class:`sqlalchemy.orm.query.Query` with the list of matching file or dataset ids
    """

    subq = match_query(query, latest, **kwargs)
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

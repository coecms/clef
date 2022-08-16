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
Functions for searching the ESGF and matching the results against the local DB 
database

* :func:`esgf_query` performs a query against the ESGF web API.
* :func:`match_query` performs an outer join of the :func:`esgf_query` results
  against the :class:`clef.model.Path` table
* :func:`find_local_path` and :func:`find_missing_id` use the results of
  :func:`match_query` to return the files that are replicated locally and
  missing from the replica respectively.
"""


import requests
import sys
import sqlalchemy as sa
import pandas as pd

from sqlalchemy.sql import column
from sqlalchemy.sql import values as sqlalvalues
from sqlalchemy import String, Float, Integer, or_, func

#from .pgvalues import values
from .model import Path, Checksum
from .exception import ClefException


class ESGFException(ClefException):
    """Error from the ESGF API
    """
    pass


def esgf_query(query=None, fields=[], otype='File', limit=10000, offset=0,  distrib=True, replica=False, latest=None,  **kwargs):
    """Search the ESGF

    Searches the ESGF using its `API
    <https://github.com/ESGF/esgf.github.io/wiki/ESGF_Search_REST_API>`_.
    Keyword arguments not listed here are passed on to the API search, they can
    either be single values or lists.

    Args:
        query (str): Full text query
        fields (list): Fields to return
        limit (int): Maximum items to return
        offset (int): Starting offset of returned items (use with limit for paging)
        distrib (bool): Distribute the search across all nodes
        replica (bool): Return replicated datasets
        latest (bool or None): Return only latest (True), only not latest (False) or all versions (None)
        **kwargs: See the `ESGF API docs <https://github.com/ESGF/esgf.github.io/wiki/ESGF_Search_REST_API>`_

    Returns:
        API response from ESGF, decoded from JSON into a Python dict
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
          'type': otype,
          'format': 'application/solr+json',
          }
    params.update(kwargs)
    if otype == 'Dataset': params.pop('type')

    try:
        r = requests.get('https://esgf.nci.org.au/esg-search/search',
                     params = params )
        r.raise_for_status()
    except Exception as err:
        r = requests.get(f'https://esgf-node.llnl.gov/esg-search/search',
                     params = params )
        r.raise_for_status()
    except Exception as err:
        raise ESGFException(f'Currently is not possible to contact one of the ESGF nodes try again later or use --local option') 
    return r.json()


def link_to_esgf(query, **kwargs):
    """Convert search terms to a ESGF search URL

    Returns a link to the user-facing ESGF web search matching a particular
    query. This is helpful for error messages, users can follow the URL to find
    the matches as ESGF sees them

    Note that this link is to the ESGF user-facing search page, rather than the
    web API that :func:`esgf_query` uses.

    Args:
        **kwargs: As :func:`esgf_query`

    Returns:
        str: URL to the ESGF search website
    """

    constraints = {k: v for k,v in kwargs.items() if v != ()}
    params = {
            'query': query,
            'fields': kwargs.get('fields',None),
            'offset': kwargs.get('offset',None),
            'limit': kwargs.get('limit',None),
            'type': kwargs.get('otype','File'),
            'distrib': 'on' if kwargs.get('distrib',True) else None,
            'replica': 'on' if kwargs.get('replica',False) else None,
            'latest': 'on' if kwargs.get('latest',None) else None
            }
    params.update(constraints)

    #r = requests.Request('GET','https://esgf-node.llnl.gov/search/%s'%endpoint,
    #r = requests.Request('GET','https://esgf-data.dkrz.de/search/%s-dkrz'%endpoint,
    r = requests.Request('GET','https://esgf.nci.org.au/search/esgf-nci',
            params=params,
            )
    return r.prepare().url


def find_checksum_id(query, **kwargs):
    """Get checksums and IDs of matching files from ESGF

    Searches ESGF using :func:`esgf_query`, then converts the response into a
    SQLAlchemy selectable for further processing

    Args:
        **kwargs: See :func:`esgf_query`

    Returns:
        Values table of matching File objects, containing
         * checksum
         * id
         * dataset_id
         * title
         * version
        This table can be joined against the DB database tables
    """
    constraints = {k: v for k,v in kwargs.items() if v != ()}
    response = esgf_query(query, 'checksum,id,dataset_id,title,version', **constraints)

    if response['response']['numFound'] == 0:
        raise ESGFException('No matches found on ESGF, check at %s'%link_to_esgf(query, **constraints))

    if response['response']['numFound'] > int(response['responseHeader']['params']['rows']):
        raise ESGFException('Too many results (%d), try limiting your search %s'%(response['response']['numFound'], 
                            link_to_esgf(query, **constraints)))
    # separate records that do not have checksum in response (nosums list) from others (records list)
    # we should call local_search for these i.e. a search not based on checksums but is not yet implemented
    nosums=[]
    records=[]
    # another issue appears when latest=False, then the ESGF return in the response all the variables in same dataset-id, this happens with CMIP5
    no_filter = True
    if ( constraints.get('project', None) == 'CMIP5' and constraints.get('latest', None) is False 
         and constraints.get('variable', None) is not None ):
        matches_list = ['.'+var+'_' for var in constraints.get('variable', []) ]
        no_filter = False

    for doc in response['response']['docs']:
        if  no_filter or any(st in doc['id'] for st in matches_list):
            if 'checksum' in doc.keys():
                records.append(doc)
            else:
                nosums.append(doc)

    record_list = [ 
             (doc['checksum'][0],
              doc['id'].split('|')[0], # drop the server name
              doc['dataset_id'].split('|')[0], # Drop the server name
              doc['title'],
              doc['version'],
              doc['score'])
            for doc in records]
    table = sqlalvalues(
            column('checksum', String),
            column('id', String),
            column('dataset_id', String),
            column('title', String),
            column('version', Integer),
            column('score', Float),
            name = 'esgf_table'
        ).data(record_list)

    return table


def match_query(session, query, latest=None, **kwargs):
    """Match ESGF results against :class:`clef.model.Path`

    Matches the results of :func:`find_checksum_id` with the :class:`Path`
    table. If `latest` is True the checksums will be matched, otherwise only
    the file name is used in order to spot outdated versions that have been
    removed from ESGF.

    Args:
        latest (bool): Match the checksums (True) or filenames (False)
        **kwargs: See :func:`esgf_query`

    Returns:
        Joined result of :class:`clef.model.Path` and :func:`find_checksum_id`
    """
    checksum_table = find_checksum_id(query, latest=latest, **kwargs)

    if latest is True:
        # Exact match on checksum
        return (checksum_table
                .outerjoin(Checksum,
                    or_(Checksum.md5 == checksum_table.c.checksum,
                        Checksum.sha256 == checksum_table.c.checksum))
                .outerjoin(Path))
    else:
        # Match on file name
        #return values.outerjoin(Path, Path.path.like('%/'+values.c.title))
        #return values.outerjoin(Path, func.regexp_replace(Path.path, '^.*/', '') == values.c.title)
        return checksum_table.join(Path, func.regexp_replace(Path.path, '^.*/', '') == checksum_table.c.title)

def find_local_path(session, subq):
    """Find the filesystem paths of ESGF matches

    Converts the results of :func:`match_query` to local filesystem paths,
    either to the file itself or to the containing dataset.

    Args:
        subq: result of func:`esgf_query`

    Returns:
        Iterable of strings with the paths to either paths or datasets
    """

    return (session
            .query(func.regexp_replace(subq.c.esgf_paths_path, '[^//]*$', ''))
            .select_from(subq)
            .filter(subq.c.esgf_paths_file_id != None)
            .filter(sa.not_(sa.and_(
                subq.c.esgf_paths_path.like('/g/data/rr3/publications/CMIP5/%'),
                sa.not_(subq.c.esgf_paths_path.like('/g/data/rr3/publications/CMIP5/%/files/%')))))
            .filter(sa.not_(sa.and_(
                subq.c.esgf_paths_path.like('/g/data/fs38/publications/CMIP6/%'),
                sa.not_(subq.c.esgf_paths_path.like('/g/data/fs38/publications/CMIP6/%/files/%'))
            )))
            .distinct())


def find_missing_id(session, subq):
    """
    Returns the ESGF id for each file in the ESGF query that doesn't have a
    local match

    Args:
        subq: result of func:`esgf_query`

    Returns:
        Iterable of strings with the ESGF file or dataset id
    """

    esgf_ds_id = column('dataset_id')
    return (session
            .query(esgf_ds_id)
            .select_from(subq)
            .filter(subq.c.esgf_paths_file_id == None)
            .distinct())


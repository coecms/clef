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
from sqlalchemy.sql import column
from sqlalchemy import String
from .pgvalues import values

def esgf_query(query, fields, limit=100, offset=0):
    """
    Search the ESGF
    """
    r = requests.get('https://esgf.nci.org.au/esg-search/search',
            params = {
                'query': query,
                'fields': fields,
                'offset': offset,
                'limit': limit,
                'format': 'application/solr+json',
                })

    r.raise_for_status()

    return r.json()

def id_response_to_values(response):
    """
    Convert a ESGF response into a postgresql VALUES statement
    """
    table = values([
            column('checksum', String),
            column('checksum_type', String),
            column('id', String),
        ],
        *[(doc['checksum'][0], doc['checksum_type'][0], doc['id']) 
            for doc in response['response']['docs']],
        alias_name = 'esgf',
        )

def find_local(session, query):
    r = esgf_query(query, 'checksum,checksum_type,id')
    
    values = id_response_to_values(r)

    session.query(Paths.path).join(Checksum).filter(Checksum.json[values.c.checksum_type].astext == values.c.checksum)

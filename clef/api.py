#!/usr/bin/env python
"""
file:   clef/api.py
author: Scott Wales <scott.wales@unimelb.edu.au>

Copyright 2018 ARC Centre of Excellence for Climate Systems Science

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

from clef.model import Path, ExtendedMetadata
from clef.esgf import esgf_query, match_query, link_to_esgf
from clef.db import connect, Session
from sqlalchemy.sql.expression import column, or_
from argparse import ArgumentParser


def esgf_search_cli():
    parser = ArgumentParser()
    parser.add_argument('--facet', nargs=2, action='append')
    args = parser.parse_args()

    facet_list = esgf_query(limit=0, facets='*')
    
    facets = {}
    for key, value in args.facet:
        if ((key not in facet_list['responseHeader']['params']['facet.field'])
                or value not in facet_list['facet_counts']['facet_fields'][key]):
            raise Exception(f"Bad Facet {key}:{value}")

        facets[key] = value

    connect()
    s = Session()

    q = esgf_search(s, **facets)

    local = q.filter(Path.path != None)
    local_files = local.with_entities(Path.path)
    
    absent = q.filter(Path.path == None)
    absent_files = absent.with_entities('id')
    absent_datasets = absent.distinct('dataset_id').with_entities('dataset_id')

    print(f"ESGF Query: {link_to_esgf(**facets)}")

    print("\nLocal Files:")
    for row in local_files:
        print(f"  - {row.Path.path}")

    print("\nAbsent Files:")
    for row in absent_files:
        print(f"  - {row.id}")

    print("\nAbsent Datasets:")
    for row in absent_datasets:
        print(f"  - {row.dataset_id}")

    print("\nCounts:")
    print("  local: ",local.count())
    print("  absent: ",absent.count())
    print("  total: ",q.count())



def esgf_search(session, **kwargs):
    """
    Returns a SQLAlchemy query containing the results of a file search on ESGF
    matched against the MAS database

    Returned items have the following attributes:
     * id: ESGF file ID
     * dataset_id: ESGF dataset ID
     * Path: :obj:`clef.model.Path` matching that ESGF file ID

    If a file is not present on MAS the Path attribute will be `None`, you can
    filter this with e.g.::

        r = esgf_query(session, **query).filter(Path != None)

        for m in r:
            print(m.id, m.dataset_id, m.Path.path)

    You can use joins to get more information on each file, e.g.

        r = (esgf_query(session, **query)
                .with_entities('id', model.Path, model.C5Dataset)
                .join(model.Path.c5dataset))

        for m in r:
            print(m.id, m.Path.path, m.C5Dataset.model)

    will return the ESGF file id, :obj:`clef.model.Path` and
    :obj:`clef.model.C5Dataset` for each match. Using a join is much faster
    than accessing the `c5dataset` of each match one at a time.

    Args:
        session (:obj:`clef.db.Session`): MAS Database session
        **kwargs: Passed to :func:`clef.esgf.esgf_query`

    Returns:
        :obj:`sqlalchemy.orm.query.Query` with columns 'id', 'dataset_id' and 'Path'.
    """

    # Get ESGF results
    matched_q = match_query(session, latest=True, **kwargs)
    
    # Query the database for matches
    q = (session.
            query(
                column('id'),
                column('dataset_id'),
                Path,
                )
            .select_from(matched_q))

    if 'variable' in kwargs:
        # Handle bad ACCESS results
        q = (q
                .outerjoin(Path.extended)
                .filter(or_(Path.path == None, ExtendedMetadata.variable == kwargs['variable'])))

    return q

if __name__ == '__main__':
    esgf_search_cli()

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

from clef.db import connect, Session
from clef.code import local_query

def export(local_query):
    for match in local_query:
        ds = xarray.open_dataset(sorted(match['filenames']))
        print(ds)

if __name__ == '__main__':
    connect(user='saw562')

    s = Session()

    q = local_query(s, model='ACCESS1.0', experiment='historical', variable='tas')

    export(q)

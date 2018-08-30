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

from clef.model import *

import six


def test_checksum(session):
    r = session.query(Checksum).first()

    assert isinstance(r.md5, six.string_types)
    assert isinstance(r.sha256, six.string_types)
    assert isinstance(r.path.path, six.string_types)

def test_netcdf(session):
    r = session.query(Netcdf).first()


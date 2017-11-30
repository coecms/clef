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

import keyring
from .git_keyring import GitCredentialCacheKeyring
keyring.set_keyring(GitCredentialCacheKeyring())

from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import sessionmaker
from getpass import getpass
from .model import Base

engine = None
Session = sessionmaker(bind=engine)

def connect(url='postgresql://130.56.244.107:5432/postgres', user=None, debug=False):
    """
    Connect to a database
    """
    _url = make_url(url)

    manual_password = False

    if user is not None:
        """
        Manually specified user
        """
        _url.username = user
        _url.password = ''
        _url.password = keyring.get_password('arccssive2', user)
        if _url.password is None:
            _url.password = getpass("Password for user %s: "%user)

    engine = create_engine(_url, echo=debug)
    Session.configure(bind=engine)

    return engine

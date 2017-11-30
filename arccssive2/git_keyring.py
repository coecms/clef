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
import keyring.backend
import subprocess

class GitCredentialCacheKeyring(keyring.backend.KeyringBackend):
    """
    Store credentials in git memory cache

    https://git-scm.com/book/gr/v2/Git-Tools-Credential-Storage
    """
    priority = 1

    def set_password(self, servicename, username, password):
        self._call_keyring('store', servicename, username, password)

    def get_password(self, servicename, username):
        message = self._call_keyring('get', servicename, username)
        for line in message.splitlines():
            key, value = line.split('=')
            if key == 'password':
                return value

    def delete_password(self, servicename, username):
        self._call_keyring('erase', servicename, username)

    def _call_keyring(self, action, host, username, password=None, protocol='python_keyring'):
        message = ("protocol=%s\nhost=%s\nusername=%s\npassword=%s\n"%(
            protocol,host,username,password)
            ).encode('utf-8')
        return subprocess.check_output(
                ['git','credential-cache',action],
                input=message
                ).decode('utf-8')

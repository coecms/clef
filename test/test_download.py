#!/usr/bin/env python
#
# Copyright 2019 Scott Wales
#
# Author: Scott Wales <scott.wales@unimelb.edu.au>
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

from clef.download import write_request, helpdesk
from unittest.mock import patch
from smtplib import SMTPException
import builtins

def test_helpdesk(tmp_path):
    request = tmp_path / 'request'
    request.write_text("Dummy Request")

    with patch('clef.download.smtplib.SMTP') as smtp:
        helpdesk('dummy_user', tmp_path, 'request', 'dummy_project')
        smtp.assert_called_once()
        smtp.reset_mock()

        inst = smtp.return_value
        inst.sendmail.side_effect = SMTPException
        helpdesk('dummy_user', tmp_path, 'request', 'dummy_project')
        smtp.assert_called_once()
        inst.sendmail.assert_called_once()


def test_write_request(tmp_path):
    with patch('clef.download.os.getcwd', return_value= tmp_path):
        with patch('clef.download.helpdesk') as helpdesk_:
            with patch('clef.download.platform.node', return_value='vdi'):
                with patch.object(builtins, 'input', return_value='y'):
                    write_request('dummy_project', ['a','b'])
                    helpdesk_.assert_called_once()

                helpdesk_.reset_mock()
                with patch.object(builtins, 'input', return_value='n'):
                    write_request('dummy_project', ['a','b'])
                    helpdesk_.assert_not_called()


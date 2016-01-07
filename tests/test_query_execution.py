# Copyright 2015 Measurement Lab
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

import os
import subprocess
import sys
import unittest

import mock

sys.path.insert(1, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../bigsanity')))
import query_execution

MOCK_QUERY = 'mock SQL query string'


class QueryExecutorTest(unittest.TestCase):

    def setUp(self):
        # Mock out calls to subprocess.Popen.
        subprocess_popen_patch = mock.patch.object(subprocess,
                                                   'Popen',
                                                   autospec=True)
        self.addCleanup(subprocess_popen_patch.stop)
        subprocess_popen_patch.start()

        self.test_execute = query_execution.QueryExecutor().execute_query

    def test_execute_query_when_query_yields_results(self):
        """When query yields results, pass results through to the caller."""
        mock_results = 'a,b\n123,456\n'
        mock_process = mock.Mock(returncode=0)
        mock_process.communicate.return_value = [mock_results,
                                                 'mock stderr output']
        subprocess.Popen.return_value = mock_process
        self.assertEqual(mock_results, self.test_execute(MOCK_QUERY))

    def test_execute_query_when_query_yields_no_results(self):
        """When query yields no results, return value should be empty string."""
        mock_process = mock.Mock(returncode=0)
        mock_process.communicate.return_value = ['', 'mock stderr output']
        subprocess.Popen.return_value = mock_process
        self.assertEqual('', self.test_execute(MOCK_QUERY))

    def test_execute_query_when_bq_is_not_installed(self):
        """If we can't execute bq, show a more helpful error."""
        subprocess.Popen.side_effect = OSError('mock OSError')
        with self.assertRaises(query_execution.BqNotInstalledError):
            self.test_execute(MOCK_QUERY)

    def test_execute_query_when_bq_fails(self):
        """If bq fails exits with nonzero return code, raise an exception."""
        mock_process = mock.Mock(returncode=-1)
        mock_process.communicate.return_value = ['mock stdout output',
                                                 'mock stderr output']
        subprocess.Popen.return_value = mock_process
        with self.assertRaises(query_execution.BqFailedError):
            self.test_execute(MOCK_QUERY)


if __name__ == '__main__':
    unittest.main()

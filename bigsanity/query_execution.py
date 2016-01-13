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

import subprocess


class Error(Exception):
    pass


class BqNotInstalledError(Error):
    """Error raised when the bq utility seems to not be installed."""

    def __init__(self):
        super(BqNotInstalledError, self).__init__(
            'Failed to execute bq command line utility. '
            'Is bq installed? '
            'https://cloud.google.com/bigquery/bq-command-line-tool')


class BqFailedError(Error):
    """Error raised when the bq utility fails."""

    def __init__(self, query):
        super(
            BqFailedError,
            self).__init__('bq failed when attempt to execute query:\n' + query)


class QueryExecutor(object):

    def execute_query(self, query):
        """Executes a BigQuery query and returns the results in CSV format.

        Note: This is a temporary, basic implementation of BigQuery
        communication to last through BigSanity M1 and M2. This will be replaced
        in M3 by an implementation that communicates with BigQuery through
        programmatic APIs rather than command-line tools.

        Args:
            query: A BigQuery SQL string containing a query to execute.

        Returns:
            The result of the query in CSV format.
        """
        bq_params = [
            'query', '--format=csv', '--headless', '--quiet',
            '--max_rows=2000000000'
        ]
        try:
            bq_proc = subprocess.Popen(['bq'] + bq_params,
                                       stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
        except OSError:
            raise BqNotInstalledError()
        result = bq_proc.communicate(query)[0]
        if bq_proc.returncode != 0:
            raise BqFailedError(query)
        return result

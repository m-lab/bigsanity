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

import csv
import io
import formatting


def _parse_query_result(query_result):
    """Parses the results of a table equivalence query.

    Parses the output of a table equivalence query into lists of test_id values
    that failed to match between the per-month tables and the per-project table.

    Args:
        query_results: The results of a table equivalence query, in CSV format.

    Returns:
        A two-tuple where the first item is a list of test_id values that appear
        only in the per-month table(s) and the second item is a list of test_id
        values that appear only in the per-project table.
    """
    per_month_ids = []
    per_project_ids = []
    for row in csv.DictReader(io.BytesIO(query_result)):
        if row['per_month_test_id']:
            per_month_ids.append(row['per_month_test_id'])
        if row['per_project_test_id']:
            per_project_ids.append(row['per_project_test_id'])
    return per_month_ids, per_project_ids


def _format_check_failure_message(per_month_ids, per_project_ids, query):
    """Creates a user-friendly message explaining an equivalence check failure.

    Args:
        per_month_ids: A list of test_id values that appeared only in the
            per-month tables.
        per_project_ids: A list of test_id values that appeared only in the
            per-project tables.
        query: The SQL query used to compare the two tables.

    Returns:
        A user-friendly message explaining the sanity check failure.
    """
    message = 'Check failed: TABLE EQUIVALENCE\n'
    if per_month_ids:
        message += ('test_id values present in per-month table, but NOT present'
                    ' in per-project table:\n')
        message += '%s\n' % formatting.indent('\n'.join(per_month_ids))
    if per_project_ids:
        message += ('test_id values present in per-project table, but NOT '
                    'present in per-month table:\n')
        message += '%s\n' % formatting.indent('\n'.join(per_project_ids))
    message += 'BigQuery SQL:\n%s' % formatting.indent(query)
    return message


class CheckResult(object):

    def __init__(self, success, message=None):
        """Represents the result of a sanity check.

        Args:
            success: True if the check succeeded.
            message: If success is True, this should be set to None. If success
                is False, this contains a message explaining the check failure.
        """
        self._success = success
        self._message = message

    @property
    def success(self):
        """Indicates whether the sanity check succeeded."""
        return self._success

    @property
    def message(self):
        """On check failure, contains a message explaining the failure."""
        return self._message


class TableEquivalenceChecker(object):
    """Checker to verify that two BigQuery tables contain equivalent rows.

    Checker to implement table equivalence checks. This acts as the glue between
    the table equivalence query generator and the query executor. It uses the
    query generator to create a table equivalence query, then uses the executor
    to retrieve the results of that query. It then parses the query results in
    order to create a CheckResult object indicating if the check failed and why.
    """

    def __init__(self, query_generator_factory, query_executor):
        """Creates a new TableEquivalenceChecker.

        Args:
            query_generator_factory: Factory to create
                TableEquivalenceQueryGenerator instances.
            query_executor: Executor for BigQuery SQL queries.
        """
        self._query_generator_factory = query_generator_factory
        self._query_executor = query_executor

    def check(self, project, time_range_start, time_range_end):
        """Perform a table equivalence check for a project in a time window.

        Given an M-Lab project and a time window, checks that the per-month
        tables and the per-project table contain equivalent data for that
        project within the time window.

        Args:
            project: Numerical ID of M-Lab project in BigQuery (e.g. NDT = 0).
            time_range_start: Start of window (inclusive) for which to generate
                query (as datetime).
            time_range_end: End of time window (not inclusive) for which to
                generate query (as datetime).

        Returns:
            A CheckResult object representing the result of the check.
        """
        query = self._query_generator_factory.create(
            project, time_range_start, time_range_end).generate_query()
        query_result = self._query_executor.execute_query(query)
        if query_result:
            # Non-empty results of the query indicates that the check failed.
            per_month_ids, per_project_ids = _parse_query_result(query_result)
            message = _format_check_failure_message(per_month_ids,
                                                    per_project_ids, query)
            return CheckResult(success=False, message=message)
        else:
            return CheckResult(success=True)

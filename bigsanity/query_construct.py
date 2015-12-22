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

import datetime
import re

import constants
import table_names


def _construct_equivalence_query(tables, conditions):
    """Constructs BigQuery SQL to be used in a table equivalence check.

    Args:
        tables: A list of BigQuery table names to query.
        conditions: A list of BigQuery WHERE clauses to apply to the query.

    Returns:
        A BigQuery SQL query corresponding to the provided parameters.
    """
    return """
SELECT
    test_id
FROM
    {tables}
WHERE
    {conditions}
ORDER BY
    test_id""".format(tables=',\n\t'.join(tables),
                      conditions='\n    AND '.join(conditions)).strip()


def _format_project_condition(project):
    return 'project = %d' % project


def _to_unix_timestamp(dt):
    """Converts a datetime to Unix timestamp."""
    return int((dt - datetime.datetime(1970, 1, 1)).total_seconds())


def _to_human_readable_date(dt):
    """Converts a datetime to a human readable date of the form YYYY-MM-DD."""
    return dt.strftime('%Y-%m-%d')


def _project_has_intermediate_snapshots(project):
    # TODO(mtlynch): This should just be applied to all web100 projects, but
    # there is currently a bug with SideStream where snapshots are
    # incorrectly marked as intermediate snapshots.
    return (project == constants.PROJECT_ID_NDT or
            project == constants.PROJECT_ID_NPAD)


class TableEquivalenceQueryGenerator(object):
    """Generates queries to test the equivalence of two M-Lab tables."""

    def __init__(self, project, time_range_start, time_range_end):
        """Creates a new TableEquivalenceQueryGenerator.

        Args:
            project: Numerical ID of M-Lab project in BigQuery (e.g. NDT = 0).
            time_range_start: Start of window (inclusive) for which to generate
                query (as datetime).
            time_range_start: End of time window (not inclusive) for which to
                generate query (as datetime).
        """
        self._project = project
        self._time_range_start = time_range_start
        self._time_range_end = time_range_end

    def generate_queries(self):
        """Generate two or more equivalance queries.

        Generates two or more equivalence queries. That is, distinct queries
        that should yield the exact same resulting data.

        Returns:
            A tuple of BigQuery SQL query strings.
        """
        return (self._generate_legacy_per_month_query(),
                self._generate_per_project_query())

    def _generate_legacy_per_month_query(self):
        conditions = []
        conditions.append(_format_project_condition(self._project))
        if _project_has_intermediate_snapshots(self._project):
            conditions.append('web100_log_entry.is_last_entry = True')
        conditions.append(self._format_time_range_condition())
        tables = table_names.legacy_monthly_tables(self._time_range_start,
                                                   self._time_range_end)
        return _construct_equivalence_query(tables, conditions)

    def _generate_per_project_query(self):
        tables = [table_names.per_project_table(self._project)]
        conditions = [self._format_time_range_condition()]
        return _construct_equivalence_query(tables, conditions)

    def _format_time_range_condition(self):
        start_time = _to_unix_timestamp(self._time_range_start)
        start_time_human = _to_human_readable_date(self._time_range_start)
        end_time = _to_unix_timestamp(self._time_range_end)
        end_time_human = _to_human_readable_date(self._time_range_end)
        return (
            '((web100_log_entry.log_time >= {start_time}) AND\t-- {start_time_human}'
            '\n\t (web100_log_entry.log_time < {end_time}))\t-- {end_time_human}'
        ).format(start_time=start_time,
                 start_time_human=start_time_human,
                 end_time=end_time,
                 end_time_human=end_time_human)

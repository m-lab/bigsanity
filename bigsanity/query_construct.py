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

import constants
import table_names


def _construct_equivalence_query(per_month_query, per_project_query):
    """Constructs BigQuery SQL to be used in a table equivalence check.

    Constructs a query composed of two subqueries that retrieve test_id values
    from per-month table(s) and a per-project table. The query yields all of the
    test_id values that appear in only one of the two tables (indicating an
    inconsistency between the tables)

    Args:
        per_month_query: A BigQuery SQL query that selects test_id values from
            the per-month tables.
        per_project_query: A BigQuery SQL query that selects test_id values from
            a per-project table.

    Returns:
        A BigQuery SQL query to test the equivalence of the two subqueries.
    """
    # Add whitespace for readable generated SQL.
    per_month_query_indented = per_month_query.replace('\n', '\n        ')
    per_project_query_indented = per_project_query.replace('\n', '\n        ')
    return """
SELECT
    per_month.test_id,
    per_project.test_id
FROM
    (
        {per_month_query_indented}
    ) AS per_month
    FULL OUTER JOIN EACH
    (
        {per_project_query_indented}
    ) AS per_project
ON
    per_month.test_id=per_project.test_id
WHERE
    per_month.test_id IS NULL
    OR per_project.test_id IS NULL""".format(
        per_month_query_indented=per_month_query_indented,
        per_project_query_indented=per_project_query_indented)


def _construct_test_id_subquery(tables, conditions):
    """Constructs BigQuery SQL to retrieve test_id values.

    Constructs a BigQuery SQL query to retrieve the test_id values from the
    specified tables with the specified set of conditions.

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
    {conditions}""".format(tables=',\n    '.join(tables),
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

    def generate_query(self):
        """Generates a query demonstrating equivalence between two table types.

        Generates a query that should yield 0 rows if the target tables contain
        equivalent data within the given time window. If the query does yield
        rows, this indicates that the tables are not equivalent. Non-NULL values
        in the per_month.test_id column indicate test_ids present in the
        per-month table that did not appear in the per-project table, while non-
        NULL values in the per_project.test_id column indicate test_ids present
        in the per-project table that did not appear in the per-month table.

        Returns:
            A BigQuery SQL statement that yields 0 rows if the per month and
            per-project tables are equivalent.
        """
        return _construct_equivalence_query(self._generate_per_month_query(),
                                            self._generate_per_project_query())

    def _generate_per_month_query(self):
        conditions = []
        conditions.append(_format_project_condition(self._project))
        if _project_has_intermediate_snapshots(self._project):
            conditions.append('web100_log_entry.is_last_entry = True')
        conditions.append(self._format_time_range_condition())
        tables = table_names.monthly_tables(self._time_range_start,
                                            self._time_range_end)
        return _construct_test_id_subquery(tables, conditions)

    def _generate_per_project_query(self):
        tables = [table_names.per_project_table(self._project)]
        conditions = [self._format_time_range_condition()]
        return _construct_test_id_subquery(tables, conditions)

    def _format_time_range_condition(self):
        start_time = _to_unix_timestamp(self._time_range_start)
        start_time_human = _to_human_readable_date(self._time_range_start)
        end_time = _to_unix_timestamp(self._time_range_end)
        end_time_human = _to_human_readable_date(self._time_range_end)
        return (
            '((web100_log_entry.log_time >= {start_time}) AND  -- {start_time_human}'
            '\n         (web100_log_entry.log_time < {end_time}))  -- {end_time_human}'
        ).format(start_time=start_time,
                 start_time_human=start_time_human,
                 end_time=end_time,
                 end_time_human=end_time_human)

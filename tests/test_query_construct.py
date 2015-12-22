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
import os
import re
import sys
import unittest

sys.path.insert(1, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../bigsanity')))
import constants
import query_construct


def _normalize_whitespace(original):
    return re.sub(r'\s+', ' ', original).strip()


def _split_and_normalize_query(query_string):
    lines = []
    for line in query_string.strip().splitlines():
        # omit blank lines
        if not line:
            continue
        lines.append(_normalize_whitespace(line))
    return lines


class QueryGeneratorTest(unittest.TestCase):

    def assertQueriesEqual(self, expected, actual):
        expected_lines = _split_and_normalize_query(expected)
        actual_lines = _split_and_normalize_query(actual)

        self.assertSequenceEqual(expected_lines, actual_lines)

    def assertQuerySetEqual(self, expected, actual):
        if len(expected) != len(actual):
            print '\n\nexpected: %s\n\nactual: %s' % ('\n'.join(expected),
                                                      '\n'.join(actual))
        self.assertEqual(len(expected), len(actual))
        for i in range(len(expected)):
            self.assertQueriesEqual(expected[i], actual[i])


class TableEquivalenceQueryGeneratorTest(QueryGeneratorTest):

    def _get_queries_actual(self, project, start_time, end_time):
        return query_construct.TableEquivalenceQueryGenerator(
            project, start_time, end_time).generate_queries()

    def test_correct_query_generation_for_ndt_full_month(self):
        """Queries on border of a month should spill into adjacent months.

        If a query's time window falls within one day of the end of the month,
        it should include tables from the adjacent months in the legacy
        per-month query.
        """
        legacy_per_month_query_expected = """
        SELECT
            test_id
        FROM
            plx.google:m_lab.2009_02.all,
            plx.google:m_lab.2009_03.all,
            plx.google:m_lab.2009_04.all
        WHERE
            project = 0
            AND web100_log_entry.is_last_entry = True
            AND ((web100_log_entry.log_time >= 1235865600) AND  -- 2009-03-01
                 (web100_log_entry.log_time <  1238544000))     -- 2009-04-01
        ORDER BY
            test_id"""

        per_project_query_expected = """
        SELECT
            test_id
        FROM
            plx.google:m_lab.ndt.all
        WHERE
            ((web100_log_entry.log_time >= 1235865600) AND  -- 2009-03-01
             (web100_log_entry.log_time <  1238544000))     -- 2009-04-01
        ORDER BY
            test_id"""

        query_set_expected = (legacy_per_month_query_expected,
                              per_project_query_expected)
        start_time = datetime.datetime(2009, 3, 1)
        end_time = datetime.datetime(2009, 4, 1)
        query_set_actual = self._get_queries_actual(constants.PROJECT_ID_NDT,
                                                    start_time, end_time)
        self.assertQuerySetEqual(query_set_expected, query_set_actual)

    def test_correct_query_generation_for_ndt_across_months(self):
        """Queries not on border of months should not spill over.

        Queries with time windows that do not start or end within one day of the
        end of month should not include tables for the adjacent month in the
        legacy per month query, even when the time window spans multiple months.
        """
        legacy_per_month_query_expected = """
        SELECT
            test_id
        FROM
            plx.google:m_lab.2009_03.all,
            plx.google:m_lab.2009_04.all
        WHERE
            project = 0
            AND web100_log_entry.is_last_entry = True
            AND ((web100_log_entry.log_time >= 1237075200) AND  -- 2009-03-15
                 (web100_log_entry.log_time <  1239753600))     -- 2009-04-15
        ORDER BY
            test_id"""

        per_project_query_expected = """
        SELECT
            test_id
        FROM
            plx.google:m_lab.ndt.all
        WHERE
            ((web100_log_entry.log_time >= 1237075200) AND  -- 2009-03-15
             (web100_log_entry.log_time <  1239753600))     -- 2009-04-15
        ORDER BY
            test_id"""

        query_set_expected = (legacy_per_month_query_expected,
                              per_project_query_expected)
        start_time = datetime.datetime(2009, 3, 15)
        end_time = datetime.datetime(2009, 4, 15)
        query_set_actual = self._get_queries_actual(constants.PROJECT_ID_NDT,
                                                    start_time, end_time)
        self.assertQuerySetEqual(query_set_expected, query_set_actual)

    def test_correct_query_generation_for_ndt_within_single_month(self):
        """Queries not on border of months should not spill over.

        When a query's time window is within a single month and does not come
        within one day of the month boundary, we should not query any adjacent
        month in the legacy per month query.
        """
        legacy_per_month_query_expected = """
        SELECT
            test_id
        FROM
            plx.google:m_lab.2009_03.all
        WHERE
            project = 0
            AND web100_log_entry.is_last_entry = True
            AND ((web100_log_entry.log_time >= 1237075200) AND  -- 2009-03-15
                 (web100_log_entry.log_time <  1237507200))     -- 2009-03-20
        ORDER BY
            test_id"""

        per_project_query_expected = """
        SELECT
            test_id
        FROM
            plx.google:m_lab.ndt.all
        WHERE
            ((web100_log_entry.log_time >= 1237075200) AND  -- 2009-03-15
             (web100_log_entry.log_time <  1237507200))     -- 2009-03-20
        ORDER BY
            test_id"""

        query_set_expected = (legacy_per_month_query_expected,
                              per_project_query_expected)
        start_time = datetime.datetime(2009, 3, 15)
        end_time = datetime.datetime(2009, 3, 20)
        query_set_actual = self._get_queries_actual(constants.PROJECT_ID_NDT,
                                                    start_time, end_time)
        self.assertQuerySetEqual(query_set_expected, query_set_actual)

    def test_correct_query_generation_for_npad(self):
        legacy_per_month_query_expected = """
        SELECT
            test_id
        FROM
            plx.google:m_lab.2009_02.all,
            plx.google:m_lab.2009_03.all,
            plx.google:m_lab.2009_04.all
        WHERE
            project = 1
            AND web100_log_entry.is_last_entry = True
            AND ((web100_log_entry.log_time >= 1235865600) AND  -- 2009-03-01
                 (web100_log_entry.log_time <  1238544000))     -- 2009-04-01
        ORDER BY
            test_id"""

        per_project_query_expected = """
        SELECT
            test_id
        FROM
            plx.google:m_lab.npad.all
        WHERE
            ((web100_log_entry.log_time >= 1235865600) AND  -- 2009-03-01
             (web100_log_entry.log_time <  1238544000))     -- 2009-04-01
        ORDER BY
            test_id"""

        query_set_expected = (legacy_per_month_query_expected,
                              per_project_query_expected)
        start_time = datetime.datetime(2009, 3, 1)
        end_time = datetime.datetime(2009, 4, 1)
        query_set_actual = self._get_queries_actual(constants.PROJECT_ID_NPAD,
                                                    start_time, end_time)
        self.assertQuerySetEqual(query_set_expected, query_set_actual)

    def test_correct_query_generation_for_sidestream(self):
        legacy_per_month_query_expected = """
        SELECT
            test_id
        FROM
            plx.google:m_lab.2014_12.all,
            plx.google:m_lab.2015_01.all
        WHERE
            project = 2
            AND ((web100_log_entry.log_time >= 1419724800) AND  -- 2014-12-28
                 (web100_log_entry.log_time <  1420243200))     -- 2015-01-03
        ORDER BY
            test_id"""

        per_project_query_expected = """
        SELECT
            test_id
        FROM
            plx.google:m_lab.sidestream.all
        WHERE
            ((web100_log_entry.log_time >= 1419724800) AND  -- 2014-12-28
             (web100_log_entry.log_time <  1420243200))     -- 2015-01-03
        ORDER BY
            test_id"""

        query_set_expected = (legacy_per_month_query_expected,
                              per_project_query_expected)
        start_time = datetime.datetime(2014, 12, 28)
        end_time = datetime.datetime(2015, 1, 3)
        query_set_actual = self._get_queries_actual(
            constants.PROJECT_ID_SIDESTREAM, start_time, end_time)
        self.assertQuerySetEqual(query_set_expected, query_set_actual)

    def test_correct_query_generation_for_paris_traceroute(self):
        legacy_per_month_query_expected = """
        SELECT
            test_id
        FROM
            plx.google:m_lab.2014_12.all,
            plx.google:m_lab.2015_01.all
        WHERE
            project = 3
            AND ((web100_log_entry.log_time >= 1419724800) AND  -- 2014-12-28
                 (web100_log_entry.log_time <  1420243200))     -- 2015-01-03
        ORDER BY
            test_id"""

        per_project_query_expected = """
        SELECT
            test_id
        FROM
            plx.google:m_lab.paris_traceroute.all
        WHERE
            ((web100_log_entry.log_time >= 1419724800) AND  -- 2014-12-28
             (web100_log_entry.log_time <  1420243200))     -- 2015-01-03
        ORDER BY
            test_id"""

        query_set_expected = (legacy_per_month_query_expected,
                              per_project_query_expected)
        start_time = datetime.datetime(2014, 12, 28)
        end_time = datetime.datetime(2015, 1, 3)
        query_set_actual = self._get_queries_actual(
            constants.PROJECT_ID_PARIS_TRACEROUTE, start_time, end_time)
        self.assertQuerySetEqual(query_set_expected, query_set_actual)


if __name__ == '__main__':
    unittest.main()

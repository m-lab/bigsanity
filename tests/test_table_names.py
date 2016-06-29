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
import sys
import unittest

sys.path.insert(1, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../bigsanity')))
import constants
import table_names


class TableNamesTest(unittest.TestCase):

    def test_per_project_table(self):
        """Generate valid table names for valid project IDs."""
        self.assertEqual(
            'plx.google:m_lab.ndt.all',
            table_names.per_project_table(constants.PROJECT_ID_NDT))
        self.assertEqual(
            'plx.google:m_lab.npad.all',
            table_names.per_project_table(constants.PROJECT_ID_NPAD))
        self.assertEqual(
            'plx.google:m_lab.sidestream.all',
            table_names.per_project_table(constants.PROJECT_ID_SIDESTREAM))
        self.assertEqual('plx.google:m_lab.paris_traceroute.all',
                         table_names.per_project_table(
                             constants.PROJECT_ID_PARIS_TRACEROUTE))

    def test_per_project_table_rejects_invalid_projects(self):
        """Reject invalid M-Lab project IDs."""
        with self.assertRaises(ValueError):
            table_names.per_project_table(500)

    def test_monthly_tables_rejects_invalid_dates(self):
        """Reject invalid table dates."""
        # 2009-01-31 is before M-Lab epoch.
        with self.assertRaises(ValueError):
            table_names.monthly_tables(
                datetime.datetime(2009, 1, 31), datetime.datetime(2009, 3, 1))
        # It should never be possible to generate table names for future dates.
        with self.assertRaises(ValueError):
            table_names.monthly_tables(
                datetime.datetime.now(),
                datetime.datetime.now() + datetime.timedelta(days=1))

    def test_monthly_tables(self):
        """Generate monthly table names for valid date range."""
        self.assertSequenceEqual(
            ('plx.google:m_lab.2009_02.all', 'plx.google:m_lab.2009_03.all'),
            table_names.monthly_tables(
                datetime.datetime(2009, 2, 11), datetime.datetime(2009, 3, 1)))

        # Rounding down to 2009-02-01 is okay even though M-Lab epoch is
        # 2009-02-11 because the 2009_02 table still exists.
        self.assertSequenceEqual(
            ('plx.google:m_lab.2009_02.all',), table_names.monthly_tables(
                datetime.datetime(2009, 2, 1), datetime.datetime(2009, 2, 15)))

        # Including the 1-day buffer, 2012-01-01 spills over into the previous
        # month's table.
        self.assertSequenceEqual(
            ('plx.google:m_lab.2011_12.all', 'plx.google:m_lab.2012_01.all',
             'plx.google:m_lab.2012_02.all'), table_names.monthly_tables(
                 datetime.datetime(2012, 1, 1), datetime.datetime(2012, 2, 1)))


if __name__ == '__main__':
    unittest.main()

# Copyright 2016 Measurement Lab
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

from dateutil import relativedelta
import mock

sys.path.insert(1, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../bigsanity')))
import cli


class CliTest(unittest.TestCase):

    def test_parse_date_arg_succeeds_when_date_has_valid_format(self):
        self.assertEqual(
            datetime.datetime(2016, 1, 11), cli.parse_date_arg('2016-01-11'))

    def test_parse_date_arg_raises_error_on_invalid_format(self):
        with self.assertRaises(ValueError):
            # Missing days part.
            cli.parse_date_arg('2016-01')
        with self.assertRaises(ValueError):
            # Invalid month (31).
            cli.parse_date_arg('2016-31-05')
        with self.assertRaises(ValueError):
            # Empty string.
            cli.parse_date_arg('')

    def test_parse_interval_days_arg_succeeds_with_valid_arg(self):
        self.assertEqual(
            relativedelta.relativedelta(days=1),
            cli.parse_interval_days_arg('1'))
        self.assertEqual(
            relativedelta.relativedelta(days=100),
            cli.parse_interval_days_arg('100'))

    def test_parse_interval_days_arg_raises_error_when_arg_is_not_positive(
            self):
        """Zero or negative values for time should raise a ValueError."""
        with self.assertRaises(ValueError):
            cli.parse_interval_days_arg('-5')
        with self.assertRaises(ValueError):
            cli.parse_interval_days_arg('0')

    def test_parse_interval_months_arg_succeeds_with_valid_arg(self):
        self.assertEqual(
            relativedelta.relativedelta(months=1),
            cli.parse_interval_months_arg('1'))
        self.assertEqual(
            relativedelta.relativedelta(months=36),
            cli.parse_interval_months_arg('36'))

    def test_parse_interval_months_arg_raises_error_when_arg_is_not_positive(
            self):
        """Zero or negative values for time should raise a ValueError."""
        with self.assertRaises(ValueError):
            cli.parse_interval_months_arg('-5')
        with self.assertRaises(ValueError):
            cli.parse_interval_months_arg('0')

    def test_get_interval_when_days_specified(self):
        interval_days = relativedelta.relativedelta(days=5)
        mock_args = mock.Mock(interval_days=relativedelta.relativedelta(days=5),
                              interval_months=None)
        self.assertEqual(interval_days, cli.get_interval(mock_args))

    def test_get_interval_when_months_specified(self):
        interval_months = relativedelta.relativedelta(months=3)
        mock_args = mock.Mock(
            interval_days=None,
            interval_months=relativedelta.relativedelta(months=3))
        self.assertEqual(interval_months, cli.get_interval(mock_args))

    def test_get_interval_raises_error_when_no_interval_is_specified(self):
        mock_args = mock.Mock(interval_days=None, interval_months=None)
        with self.assertRaises(ValueError):
            cli.get_interval(mock_args)


if __name__ == '__main__':
    unittest.main()

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

sys.path.insert(1, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../bigsanity')))
import intervals


class IntervalsTest(unittest.TestCase):

    def test_date_limits_to_intervals_when_limit_is_exactly_one_interval(self):
        intervals_expected = [(datetime.datetime(2015, 1, 1),
                               datetime.datetime(2015, 2, 1))]
        intervals_actual = intervals.date_limits_to_intervals(
            datetime.datetime(2015, 1, 1),
            datetime.datetime(2015, 2, 1),
            relativedelta.relativedelta(months=1))
        self.assertSequenceEqual(intervals_expected, intervals_actual)

    def test_date_limits_to_intervals_when_limit_is_exactly_three_intervals(
            self):
        intervals_expected = [
            (datetime.datetime(2015, 1, 1), datetime.datetime(2015, 2, 1)),
            (datetime.datetime(2015, 2, 1), datetime.datetime(2015, 3, 1)),
            (datetime.datetime(2015, 3, 1), datetime.datetime(2015, 4, 1)),
        ]
        intervals_actual = intervals.date_limits_to_intervals(
            datetime.datetime(2015, 1, 1),
            datetime.datetime(2015, 4, 1),
            relativedelta.relativedelta(months=1))
        self.assertSequenceEqual(intervals_expected, intervals_actual)

    def test_date_limits_to_intervals_when_limit_is_one_and_a_half_intervals(
            self):
        """Intervals should never extend past the end date."""
        intervals_expected = [
            (datetime.datetime(2015, 1, 1), datetime.datetime(2015, 2, 1)),
            (datetime.datetime(2015, 2, 1), datetime.datetime(2015, 2, 16)),
        ]
        intervals_actual = intervals.date_limits_to_intervals(
            datetime.datetime(2015, 1, 1),
            datetime.datetime(2015, 2, 16),
            relativedelta.relativedelta(months=1))
        self.assertSequenceEqual(intervals_expected, intervals_actual)

    def test_date_limits_to_intervals_when_limit_is_less_than_one_interval(
            self):
        """Intervals should never extend past the end date."""
        intervals_expected = [(datetime.datetime(2015, 1, 1),
                               datetime.datetime(2015, 1, 21))]
        intervals_actual = intervals.date_limits_to_intervals(
            datetime.datetime(2015, 1, 1),
            datetime.datetime(2015, 1, 21),
            relativedelta.relativedelta(months=1))
        self.assertSequenceEqual(intervals_expected, intervals_actual)


if __name__ == '__main__':
    unittest.main()

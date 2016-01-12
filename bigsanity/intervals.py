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


def date_limits_to_intervals(date_start, date_end, date_step):
    """Convert a date range and step to a series of date intervals.

    Given a date start, end, and step, creates a list of 2-tuples of
    (start, end) times to fill up the date range. Note that date_end takes
    precedence over date_step (i.e. we never generate a date range that is
    after date_end).

    For example:

        date_limits_to_intervals(
            datetime.datetime(2015, 1, 1),
            datetime.datetime(2015, 4, 1),
            relativedelta.relativedelta(months=1))

    would yield:

        [(datetime.datetime(2015, 1, 1),
          datetime.datetime(2015, 2, 1)),
         (datetime.datetime(2015, 2, 1),
          datetime.datetime(2015, 3, 1)),
         (datetime.datetime(2015, 3, 1),
          datetime.datetime(2015, 4, 1)),]

    Args:
        date_start: A datetime indicating the start of the date range
            (inclusive).
        date_end: A datetime indicating the end of the date range (exclusive).
        date_step: A relativedelta indicating how large the date intervals
            should be. This must be a positive delta.

    Returns:
        A list of 2-tuples of (start, end) datetimes to fill the date range.
    """
    intervals = []
    interval_start = date_start
    while interval_start < date_end:
        interval_end = min(interval_start + date_step, date_end)
        intervals.append((interval_start, interval_end))
        interval_start = interval_end
    return intervals

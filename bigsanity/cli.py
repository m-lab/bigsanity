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
"""Utility functions to assist in implementing the CLI.

Constants and functions used to interact with the user via the CLI.
"""

import datetime

from dateutil import relativedelta

# Format of dates when entered as command line arguments or printed to the
# console.
DATE_FORMAT = '%Y-%m-%d'


def parse_date_arg(date_arg):
    """Parses a date command line parameter string into a datetime."""
    return datetime.datetime.strptime(date_arg, DATE_FORMAT)


def parse_interval_arg(interval_arg):
    """Parses an interval command line parameter string into an interval.

    Args:
       interval_arg: An interval string in the form of
           "[numeric_value]_[time_unit]". For example "3_months". Time units
           supported are: "days" and "months". The numeric value must be a
           positive integer.

    Returns:
        A relativedelta value parsed from the time interval.
    """
    value_str, units = interval_arg.split('_')
    value = int(value_str)
    if value <= 0:
        raise ValueError('Interval value must be a positive number: %d' % value)
    units_to_interval = {
        'days': relativedelta.relativedelta(days=value),
        'months': relativedelta.relativedelta(months=value),
    }
    if units not in units_to_interval:
        raise ValueError('Unrecognized time units: %s. Supported units: %s' %
                         (units, units_to_interval.keys()))
    return units_to_interval[units]

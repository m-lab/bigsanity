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


def parse_interval_days_arg(days_arg):
    """Parses the interval days command line string into an interval.

    Args:
       days_arg: A string representing a number of days in an interval.

    Returns:
        A relativedelta value parsed from the time interval.

    Raises:
        ValueError: If the supplied days argument is not positive.
    """
    days = int(days_arg)
    if days <= 0:
        raise ValueError('Interval value must be a positive number: %d' % days)
    return relativedelta.relativedelta(days=days)


def parse_interval_months_arg(months_arg):
    """Parses the interval months command line string into an interval.

    Args:
       months_arg: A string representing a number of months in an interval.

    Returns:
        A relativedelta value parsed from the time interval.

    Raises:
        ValueError: If the supplied months argument is not positive.
    """
    months = int(months_arg)
    if months <= 0:
        raise ValueError('Interval value must be a positive number: %d' %
                         months)
    return relativedelta.relativedelta(months=months)


def get_interval(args):
    """Given BigSanity's command line arguments, retrieves the interval value.

    Retrieves the correct interval value from among BigSanity's interval command
    line options. This is necessary as an interval parameter is required, but
    argparse does not offer support for mutually-exclusive parameters where at
    least one is required.

    Args:
        args: Command line arguments parsed from the command line by argparse.

    Returns:
        The value of the selected

    Raises:
        ValueError: If the user did not specify a value for the
            --interval_days or --interval_months parameters.
    """
    if args.interval_days:
        return args.interval_days
    elif args.interval_months:
        return args.interval_months
    else:
        raise ValueError(
            'Must specify at least one of --interval_days or --interval_months')

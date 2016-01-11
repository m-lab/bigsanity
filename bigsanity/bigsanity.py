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

import argparse
import datetime
import logging
import sys

import cli
import query_construct
import query_execution
import check_table_equivalence

logger = logging.getLogger(__name__)
LOG_FORMAT = (
    '%(asctime)-15s %(levelname)-5s %(module)s.py:%(lineno)-d %(message)s')


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


def _is_sane(project, date_start, date_end, date_step):
    """Performs sanity checks on all the time windows in the given range.

    Performs all BigSanity sanity checks on the M-Lab BigQuery tables for the
    given project and the given time range.

    Args:
        project: Numerical ID of M-Lab project in BigQuery (e.g. NDT = 0).
        date_start: Limits checks to M-Lab tests that occurred on or after this
            date.
        date_end: Limits checks to M-Lab tests that occurred before this date.

    Returns:
        True if all sanity checks pass.
    """
    checker = check_table_equivalence.TableEquivalenceChecker(
        query_construct.TableEquivalenceQueryGeneratorFactory(),
        query_execution.QueryExecutor())
    found_error = False
    check_windows = date_limits_to_intervals(date_start, date_end, date_step)
    for date_range_start, date_range_end in check_windows:
        logger.info('Checking cross-table consistency for project=%d, %s -> %s',
                    project, date_range_start.strftime(cli.DATE_FORMAT),
                    date_range_end.strftime(cli.DATE_FORMAT))
        check_result = checker.check(project, date_range_start, date_range_end)
        if not check_result.success:
            logger.error(check_result.message)
            found_error = True
    return not found_error


def main(args):
    if args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logging.basicConfig(level=log_level, format=LOG_FORMAT)

    date_start = cli.parse_date_arg(args.start_date)
    date_end = cli.parse_date_arg(args.end_date)
    date_step = cli.parse_interval_arg(args.interval)

    project = int(args.project)
    if not _is_sane(project, date_start, date_end, date_step):
        return sys.exit(-1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='BigSanity: M-Lab BigQuery Sanity Checker',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-p',
                        '--project',
                        type=int,
                        choices=range(0, 4),
                        required=True,
                        help='ID of M-Lab project in BigQuery')
    parser.add_argument('-s', '--start_date', default='2009-02-01')
    parser.add_argument(
        '-e',
        '--end_date',
        default=datetime.datetime.now().strftime(cli.DATE_FORMAT))
    parser.add_argument(
        '-i',
        '--interval',
        required=True,
        help=('The size of the time windows for each sanity check query. Must '
              'be in the form of [numeric_value]_[time units], e.g. "2_months".'
              ' The time units "days" and "months" are supported.'))
    parser.add_argument('-v',
                        '--verbose',
                        help='Produce verbose log output',
                        action='store_true')

    args = parser.parse_args()
    main(args)

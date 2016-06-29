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
"""Generates names of M-Lab BigQuery tables."""

import datetime

from dateutil import relativedelta

import constants


def monthly_tables(time_range_start, time_range_end):
    """Returns the names of all monthly tables covering a time range.

    Returns the names of all the M-Lab BigQuery monthly tables that contain test
    data within the given time range.

    Note: Tests that occur near the border of a month (e.g. midnight on the
    first or last day of the month) may be placed in the adjacent month's table
    so we add the adjacent table if the time range falls on a month boundary.

    Args:
        time_range_start: Start of time range (as datetime).
        time_range_end: End of time range (as datetime).

    Returns:
        A list of M-Lab BigQuery tables corresponding to the given time range,
        e.g.:
            ['plx.google:m_lab.2015_01.all',
             'plx.google:m_lab.2015_02.all',
             'plx.google:m_lab.2015_03.all']
    """
    MIN_TABLE_MONTH = datetime.datetime.fromtimestamp(
        constants.MLAB_EPOCH).replace(day=1,
                                      hour=0,
                                      minute=0,
                                      second=0,
                                      microsecond=0)
    MAX_TABLE_MONTH = datetime.datetime.now()
    if not (MIN_TABLE_MONTH <= time_range_start <= MAX_TABLE_MONTH):
        raise ValueError(
            'time_range_start (%s) is out of range (must be within %s to %s)' %
            (time_range_start, MIN_TABLE_MONTH, MAX_TABLE_MONTH))
    if not (MIN_TABLE_MONTH <= time_range_end <= MAX_TABLE_MONTH):
        raise ValueError(
            'time_range_end (%s) is out of range (must be within %s to %s)' %
            (time_range_end, MIN_TABLE_MONTH, MAX_TABLE_MONTH))
    day_delta = relativedelta.relativedelta(days=1)
    tables = set()
    # We add adjacent days here because a bug in BigQuery causes a handful of
    # tests to be published in the next or previous month if their log_time is
    # very close to the month border.
    current_time = max(MIN_TABLE_MONTH, time_range_start - day_delta)
    time_limit = min(MAX_TABLE_MONTH, time_range_end + day_delta)
    # Keep incrementing current_time by 1 day until we reach the end of the
    # range. This is not optimal for efficiency, but it is simple.
    while current_time < time_limit:
        table_name = monthly_table(current_time)
        tables.add(table_name)
        current_time += day_delta
    return sorted(tables)


def monthly_table(table_time):
    """Translates a time into the corresponding monthly table.

    Args:
        table_time: Datetime to map to an M-Lab BigQuery table name.

    Returns:
        Name of the table corresponding to the given time, e.g.
        'plx.google:m_lab.2015_02.all',
    """
    table_month = table_time.strftime('%Y_%m')
    return _format_table(table_month)


def per_project_table(project):
    """Returns the project-specific BigQuery table for the given project ID.

    Each M-Lab project has a project-specific table (which only includes tests
    for that project). This function translates the numeric M-Lab project ID to
    the associated project-specific table.

    Args:
        project: Numeric ID of M-Lab project, (e.g. 1).

    Returns:
        Name of project-specific table, e.g.: 'plx.google:m_lab.ndt.all'
    """
    project_id_to_name = {
        constants.PROJECT_ID_NDT: constants.PROJECT_NAME_NDT,
        constants.PROJECT_ID_NPAD: constants.PROJECT_NAME_NPAD,
        constants.PROJECT_ID_SIDESTREAM: constants.PROJECT_NAME_SIDESTREAM,
        constants.PROJECT_ID_PARIS_TRACEROUTE:
        constants.PROJECT_NAME_PARIS_TRACEROUTE,
    }
    try:
        project_name = project_id_to_name[project]
    except KeyError:
        raise ValueError('Unexpected project ID: %d' % project)
    return _format_table(project_name)


def _format_table(table_name):
    return 'plx.google:m_lab.%s.all' % table_name

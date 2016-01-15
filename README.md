[![Build
Status](https://travis-ci.org/m-lab/bigsanity.svg?branch=master)](https://travis-ci.org/m-lab/bigsanity)
[![Coverage
Status](https://coveralls.io/repos/m-lab/bigsanity/badge.svg?branch=master&service=github)](https://coveralls.io/github/m-lab/bigsanity?branch=master)

# Pre-requisites

The current version of BigSanity requires that the [`bq`
utility](https://cloud.google.com/bigquery/bq-command-line-tool) be installed
and accessible through the user's `PATH` environment variable.

To install BigSanity's required Python packages:

`pip install -r requirements.txt`

To install the Python packages required to run BigSanity's test suite:

`pip install -r test-requirements.txt`

# Performing Sanity Checks

The following commands will perform full sanity checks with BigSanity from the
start of each project until the present. The interval lengths are chosen to be
large enough to minimize total number of queries, but small enough to not
exhaust BigQuery resources.

```
python bigsanity/bigsanity.py --project 0 --start_date 2009-02-11 --interval_months 5
python bigsanity/bigsanity.py --project 1 --start_date 2009-02-11 --interval_months 36
python bigsanity/bigsanity.py --project 2 --start_date 2009-08-24 --interval_days 3
python bigsanity/bigsanity.py --project 3 --start_date 2013-05-08 --interval_days 4
```

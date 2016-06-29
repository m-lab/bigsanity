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

import mock

sys.path.insert(1, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../bigsanity')))
import check_table_equivalence
import constants
import formatting
import query_construct
import query_execution

MOCK_QUERY = 'mock SQL query string'
START_TIME = datetime.datetime(2010, 1, 5)
END_TIME = datetime.datetime(2010, 1, 15)


class TableEquivalenceCheckerTest(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.query_generator = mock.Mock(
            spec=query_construct.TableEquivalenceQueryGenerator)
        self.query_generator.generate_query.return_value = MOCK_QUERY
        self.query_generator_factory = mock.Mock(
            spec=query_construct.TableEquivalenceQueryGeneratorFactory)
        self.query_generator_factory.create.return_value = self.query_generator
        self.query_executor = mock.Mock(spec=query_execution.QueryExecutor)
        self.checker = check_table_equivalence.TableEquivalenceChecker(
            self.query_generator_factory, self.query_executor)

    def test_check_succeeds_when_query_yields_zero_rows(self):
        """Table equivalence check succeeds when query results in no rows."""
        self.query_executor.execute_query.return_value = ''

        check_result = self.checker.check(constants.PROJECT_ID_NDT, START_TIME,
                                          END_TIME)
        self.assertTrue(check_result.success)
        self.assertIsNone(check_result.message)
        # Make sure the query generator was created with the right parameters.
        self.query_generator_factory.create.assert_called_with(
            constants.PROJECT_ID_NDT, START_TIME, END_TIME)
        # Make sure the query executor executes the query produced by the query
        # generator.
        self.query_executor.execute_query.assert_called_with(MOCK_QUERY)

    def test_check_fails_when_extra_ids_are_in_both_tables(self):
        """If both tables contain disjoint IDs, equivalence check fails."""
        self.query_executor.execute_query.return_value = (
            'per_month_test_id,per_project_test_id\n'
            'mock_id_1,\n'
            'mock_id_2,\n'
            ',mock_id_3')

        check_result = self.checker.check(constants.PROJECT_ID_NDT, START_TIME,
                                          END_TIME)
        self.assertFalse(check_result.success)
        self.assertMultiLineEqual(check_result.message, (
            'Check failed: TABLE EQUIVALENCE\n'
            'test_id values present in per-month table, but NOT present in '
            'per-project table:\n'
            '  mock_id_1\n'
            '  mock_id_2\n'
            'test_id values present in per-project table, but NOT present in '
            'per-month table:\n'
            '  mock_id_3\n'
            'BigQuery SQL:\n' + formatting.indent(MOCK_QUERY)))

    def test_check_fails_when_extra_ids_are_in_per_month_table_only(self):
        """If per-month table contains extra test_ids, check fails."""
        self.query_executor.execute_query.return_value = (
            'per_month_test_id,per_project_test_id\n'
            'mock_id_1,\n'
            'mock_id_2,')

        check_result = self.checker.check(constants.PROJECT_ID_NDT, START_TIME,
                                          END_TIME)
        self.assertFalse(check_result.success)
        self.assertMultiLineEqual(check_result.message, (
            'Check failed: TABLE EQUIVALENCE\n'
            'test_id values present in per-month table, but NOT present in '
            'per-project table:\n'
            '  mock_id_1\n'
            '  mock_id_2\n'
            'BigQuery SQL:\n' + formatting.indent(MOCK_QUERY)))

    def test_check_fails_when_extra_ids_are_in_per_project_table_only(self):
        """If per-project table contains extra test_ids, check fails."""
        self.query_executor.execute_query.return_value = (
            'per_month_test_id,per_project_test_id\n'
            ',mock_id_3')

        check_result = self.checker.check(constants.PROJECT_ID_NDT, START_TIME,
                                          END_TIME)
        self.assertFalse(check_result.success)
        self.assertMultiLineEqual(check_result.message, (
            'Check failed: TABLE EQUIVALENCE\n'
            'test_id values present in per-project table, but NOT present in '
            'per-month table:\n'
            '  mock_id_3\n'
            'BigQuery SQL:\n' + formatting.indent(MOCK_QUERY)))

    def test_check_trims_list_of_extra_ids_when_the_list_is_large(self):
        """When the check finds many extra test_ids, we should trim the list.

        If the list of extra test_id values is very long, we should trim it
        down, remove duplicates, and sort it.
        """
        mock_query_result = 'per_month_test_id,per_project_test_id\n'

        # Add the first 5 values out of order.
        mock_query_result += ',mock_id_03\n'
        mock_query_result += ',mock_id_00\n'
        mock_query_result += ',mock_id_02\n'
        mock_query_result += ',mock_id_04\n'
        mock_query_result += ',mock_id_01\n'

        # Add 100 more rows with duplicates.
        for i in range(0, 100):
            mock_query_result += ',mock_id_%02d\n' % i

        self.query_executor.execute_query.return_value = mock_query_result

        check_result = self.checker.check(constants.PROJECT_ID_NDT, START_TIME,
                                          END_TIME)
        self.assertFalse(check_result.success)
        self.assertMultiLineEqual(check_result.message, (
            'Check failed: TABLE EQUIVALENCE\n'
            'test_id values present in per-project table, but NOT present in '
            'per-month table:\n'
            '  mock_id_00\n'
            '  mock_id_01\n'
            '  mock_id_02\n'
            '  mock_id_03\n'
            '  mock_id_04\n'
            '  mock_id_05\n'
            '  mock_id_06\n'
            '  mock_id_07\n'
            '  mock_id_08\n'
            '  mock_id_09\n'
            '  (95 additional or duplicate test_id values omitted)\n'
            'BigQuery SQL:\n' + formatting.indent(MOCK_QUERY)))

    def test_check_raises_exception_if_generator_factory_raises_exception(self):
        """Checker should not catch any exceptions from generator factory."""
        factory = mock.Mock(
            spec=query_construct.TableEquivalenceQueryGeneratorFactory)
        factory.create.side_effect = ValueError('mock value error')
        checker = check_table_equivalence.TableEquivalenceChecker(
            factory, self.query_executor)
        with self.assertRaises(ValueError):
            checker.check(constants.PROJECT_ID_NDT, START_TIME, END_TIME)

    def test_check_raises_exception_if_generator_raises_exception(self):
        """Checker should not catch any exceptions from query generator."""
        query_generator = mock.Mock(
            spec=query_construct.TableEquivalenceQueryGenerator)
        query_generator.generate_query.side_effect = ValueError(
            'mock value error')
        factory = mock.Mock(
            spec=query_construct.TableEquivalenceQueryGeneratorFactory)
        factory.create.return_value = query_generator
        checker = check_table_equivalence.TableEquivalenceChecker(
            factory, self.query_executor)
        with self.assertRaises(ValueError):
            checker.check(constants.PROJECT_ID_NDT, START_TIME, END_TIME)

    def test_check_raises_exception_if_query_executor_raises_exception(self):
        """Checker should not catch any exceptions from query executor."""
        query_executor = mock.Mock(spec=query_execution.QueryExecutor)
        query_executor.execute_query.side_effect = ValueError(
            'mock value error')
        checker = check_table_equivalence.TableEquivalenceChecker(
            self.query_generator_factory, query_executor)
        with self.assertRaises(ValueError):
            checker.check(constants.PROJECT_ID_NDT, START_TIME, END_TIME)


if __name__ == '__main__':
    unittest.main()

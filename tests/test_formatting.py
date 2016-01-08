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

import os
import sys
import unittest

sys.path.insert(1, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../bigsanity')))
import formatting


class FormattingTest(unittest.TestCase):

    def assertIndent(self, expected, original, spaces):
        self.assertEqual(expected, formatting.indent(original, spaces))

    def test_indent_single_line(self):
        self.assertIndent('a', 'a', 0)
        self.assertIndent('  a', 'a', 2)
        self.assertIndent('    a', 'a', 4)

    def test_indent_negative_spacing_raises_exception(self):
        """indent should reject a negative value for spacing."""
        with self.assertRaises(ValueError):
            formatting.indent('a', -1)

    def test_indent_multi_line(self):
        self.assertIndent(('  a\n'
                           '    b\n'
                           '  c'),
                          ('a\n'
                           '  b\n'
                           'c'), 2)  # yapf: disable

if __name__ == '__main__':
    unittest.main()

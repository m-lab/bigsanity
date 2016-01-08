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


def indent(s, spaces=2):
    """Indent a string by prepending a specified number of space characters.

    Adds an indent to a string on each line with the specified number of spaces.
    For example:

    The following input string (pipe characters represent line starts):
        |foo
        |  bar
        |baz
    Indented two spaces becomes:
        |  foo
        |    bar
        |  baz

    Args:
        s: The string to indent.
        spaces: The number of spaces to indent. Must be >= 0.

    Returns:
        The value of s with prepended spaces on each line.

    Raises:
        ValueError: An invalid value was specified for spaces.
    """
    if spaces < 0:
        raise ValueError('spaces must be non-negative, but was %d' % spaces)
    spacing = ' ' * spaces
    return spacing + s.replace('\n', '\n' + spacing)

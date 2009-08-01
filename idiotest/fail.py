# IdioTest - idiotest/fail.py
# Copyright 2009 Dietrich Epp <depp@zdome.net>
# This source code is licensed under the GNU General Public License,
# Version 3. See gpl-3.0.txt for details.
"""IdioTest failure functions.

This has the "TestFailure" exception as well as a convenient fail()
function.
"""
import StringIO
__all__ = ['TestFailure', 'fail']

class TestFailure(Exception):
    def __init__(self, reason):
        self.reason = reason
        self.msg = StringIO.StringIO()
    def write(self, text):
        if isinstance(text, str):
            text = unicode(text)
        self.msg.write(text)

def fail(reason=None):
    raise TestFailure(reason)

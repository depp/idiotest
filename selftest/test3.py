# IdioTest - selftest/test3.py
# Copyright 2009 Dietrich Epp <depp@zdome.net>
# This source code is licensed under the GNU General Public License,
# Version 3. See gpl-3.0.txt for details.
class NotATest(object):
    def __init__(self):
        print "This shouldn't get called"

def is_a_test():
    pass

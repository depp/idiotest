# Copyright 2009, 2012 Dietrich Epp <depp@zdome.net>
# See LICENSE.txt for details.

class NotATest(object):
    def __init__(self):
        print "This shouldn't get called"

@test
def is_a_test():
    pass

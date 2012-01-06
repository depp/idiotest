# Copyright 2009, 2012 Dietrich Epp <depp@zdome.net>
# See LICENSE.txt for details.
"""IdioTest: Simple testing framework.

Simple use guide:

    import idiotest.run
    idiotest.run.run('tests')

Place a file in the 'tests' directory named 'test1.py':

    @test
    def echo_test():
        check_output(['echo', 'abc'], output='abc\n')

    @test
    def sanity_test():
        if True == False:
            fail()
"""

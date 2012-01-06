# Copyright 2012 Dietrich Epp <depp@zdome.net>
# See LICENSE.txt for details.

@test(fail=True)
def nostdin_1():
    check_output(['./nostdin'], 'Test', '')
    fail("The pipe didn't break, but that's okay")

@test(fail=True)
def nostdin_2_fail():
    check_output(['./nostdin'], 'Test', 'Bogus')

@test
def nostdout_1():
    check_output(['./nostdout'], 'Test', '')

@test(fail=True)
def nostdout_2_fail():
    check_output(['./nostdout'], 'Test', 'Bogus')

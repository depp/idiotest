# Copyright 2012 Dietrich Epp <depp@zdome.net>
# See LICENSE.txt for details.

@test
def nostdin_1():
    check_output(['./nostdin'], 'Test', '')

@test(fail=True)
def nostdin_2_fail():
    check_output(['./nostdin'], 'Test', 'Bogus')

@test
def nostdout_1():
    check_output(['./nostdout'], 'Test', '')

@test(fail=True)
def nostdout_2_fail():
    check_output(['./nostdout'], 'Test', 'Bogus')

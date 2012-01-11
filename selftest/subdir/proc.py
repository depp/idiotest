# Copyright 2012 Dietrich Epp <depp@zdome.net>
# See LICENSE.txt for details.

@test(fail=True)
def nostdin_1():
    proc.check_output(['./nostdin'], input='Test', output='')
    fail("The pipe didn't break, but that's okay")

@test(fail=True)
def nostdin_2_fail():
    proc.check_output(['./nostdin'], input='Test', output='Bogus')

@test
def nostdout_1():
    proc.check_output(['./nostdout'], input='Test', output='')

@test(fail=True)
def nostdout_2_fail():
    proc.check_output(['./nostdout'], input='Test', output='Bogus')

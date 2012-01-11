# Copyright 2009, 2012 Dietrich Epp <depp@zdome.net>
# See LICENSE.txt for details.
import os

@test
def test1_simple():
    proc.check_output(['echo', 'This is a test'], output='This is a test\n')

@test
def test2_infile():
    proc.check_output(['cat'],
                      input=file('test1.txt', 'r'),
                      output='Test 1 contents\n')

@test
def test3_outfile():
    proc.check_output(['cat', 'test1.txt'],
                      output=file('test1.txt', 'r'))

@test
def test4_inoutfile():
    proc.check_output(['cat'],
                      input=file('test1.txt', 'r'),
                      output=file('test1.txt', 'r'))

@test(fail=True)
def test5_FAIL_RETCODE():
    proc.check_output(['cat', 'nonexistant-file.txt'],
                      output='Some text\n')

@test(fail=True)
def test6_FAIL_DIFF():
    proc.check_output(['cat'],
                      input=file('test2.in.txt', 'r'),
                      output=file('test2.out.txt', 'r'))

# Copyright 2009, 2012 Dietrich Epp <depp@zdome.net>
# See LICENSE.txt for details.
import os

@test
def test1_simple():
    check_output(['echo', 'This is a test'], None, 'This is a test\n')

@test
def test2_infile():
    check_output(['cat'], '@test1.txt', 'Test 1 contents\n')

@test
def test3_outfile():
    check_output(['cat', 'test1.txt'], None, '@test1.txt')

@test
def test4_inoutfile():
    check_output(['cat'], '@test1.txt', '@test1.txt')

@test(fail=True)
def test5_FAIL_RETCODE():
    check_output(['cat', 'nonexistant-file.txt'], None, 'Some text\n')

@test(fail=True)
def test6_FAIL_DIFF():
    check_output(['cat'], '@test2.in.txt', '@test2.out.txt')

# IdioTest - selftest/check_output.py
# Copyright 2009 Dietrich Epp <depp@zdome.net>
# This source code is licensed under the GNU General Public License,
# Version 3. See gpl-3.0.txt for details.
import os

def test1_simple():
    check_output(['echo', 'This is a test'], None, 'This is a test\n')

def test2_infile():
    check_output(['cat'], '@test1.txt', 'Test 1 contents\n')

def test3_outfile():
    check_output(['cat', 'test1.txt'], None, '@test1.txt')

def test4_inoutfile():
    check_output(['cat'], '@test1.txt', '@test1.txt')

def test5_FAIL_RETCODE():
    check_output(['cat', 'nonexistant-file.txt'], None, 'Some text\n')

def test6_FAIL_DIFF():
    check_output(['cat'], '@test2.in.txt', '@test2.out.txt')
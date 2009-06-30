# CHRP - test/selftest/selftest.py
# Copyright 2009 Dietrich Epp <depp@zdome.net>
# This source code is licensed under the GNU General Public License,
# Version 3. See gpl-3.0.txt for details.
import os

TEXT = """THIS IS JUST A TEST
this line is to be changed
third line
missing line
"""

TEXT2 = """new line
THIS IS JUST A TEST
into this
third line
"""

def test_cat():
    check_output(['cat'], TEXT, TEXT)

def test_cat_fail():
    check_output(['cat'], TEXT2, TEXT)

def test_false_fail():
    check_output(['false'], None, None)

TEXT3 = "this is sample text\n"
outf = open('temp.txt', 'w')
outf.write(TEXT3)
outf.close()
def test_file():
    try:
        check_output(['cat', 'temp.txt'], None, TEXT3)
    finally:
        os.unlink('temp.txt')

def test_file_2():
    check_output(['cat', 'sample.txt'], None, 'sample text\n')

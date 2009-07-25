# IdioTest - selftest/unicode.py
# Copyright 2009 Dietrich Epp <depp@zdome.net>
# This source code is licensed under the GNU General Public License,
# Version 3. See gpl-3.0.txt for details.
def utest_FAIL():
    check_output(['cat'], '\xff\n', '\xff\fe\n')

# IdioTest - selftest/test_console.py
# Copyright 2009 Dietrich Epp <depp@zdome.net>
# This source code is licensed under the GNU General Public License,
# Version 3. See gpl-3.0.txt for details.
import time

@test
def test_sleep_succeed():
    time.sleep(1)

@test(fail=True)
def time_sleep_fail():
    time.sleep(1)
    fail("supposed to fail")

# Copyright 2009, 2012 Dietrich Epp <depp@zdome.net>
# See LICENSE.txt for details.
import time

@test
def test_sleep_succeed():
    time.sleep(1)

@test(fail=True)
def time_sleep_fail():
    time.sleep(1)
    fail("supposed to fail")

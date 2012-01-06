# Copyright 2009, 2012 Dietrich Epp <depp@zdome.net>
# See LICENSE.txt for details.
@test(fail=True)
def utest_FAIL():
    check_output(['cat'], '\xff\n', '\xff\fe\n')

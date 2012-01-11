# Copyright 2009, 2012 Dietrich Epp <depp@zdome.net>
# See LICENSE.txt for details.
@test(fail=True)
def utest_FAIL():
    proc.check_output(['cat'], input='\xff\n', output='\xff\fe\n')

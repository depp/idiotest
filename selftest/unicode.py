def utest_FAIL():
    check_output(['cat'], '\xff\n', '\xff\fe\n')


@test
def nostdin_1():
    check_output(['./nostdin'], 'Test', '')

@test
def nostdin_2_fail():
    check_output(['./nostdin'], 'Test', 'Bogus')

@test
def nostdout_1():
    check_output(['./nostdout'], 'Test', '')

@test
def nostdout_2_fail():
    check_output(['./nostdout'], 'Test', 'Bogus')

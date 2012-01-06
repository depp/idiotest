# Copyright 2012 Dietrich Epp <depp@zdome.net>
# See LICENSE.txt for details.

# This test always passes
@test
def test_1():
    if True == False:
        fail()

# This test is always skipped
@test("Test #2")
def test_2():
    skip()

# Any callable object can be a test
class MyTest(object):
    def __init__(self, message):
        self.message = message
    def __call__(self):
        fail(self.message)

test("Test #3", MyTest("Test 3 always fails"), fail=True)
test("Test #4", MyTest("Test 4 always fails"), fail=True)

@test
def test_get_output():
    # Gets the output of 'echo'
    abc = get_output(['echo', 'abc'])
    if abc != 'abc\n':
        fail()

@test
def test_check_output():
    # Cat should be idempotent
    check_output(['cat', 'test1.txt'], output='@test1.txt')

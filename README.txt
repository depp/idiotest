IdioTest: A simple testing framework
====================================

IdioTest is a simple testing framework.  Tests in IdioTest run
programs, feed those programs input, and compare the output to the
expected output.  IdioTest does not know or care what language you
write your programs in.  Tests in IdioTest are written in Python.

I originally made this into its own project because I had copies of it
in three other projects.  Here are the goals of idiotest:

  * IdioTest knows nothing about your development environment.  It
    just runs programs and checks the output.

  * IdioTest produces useful and informative messages when you need
    them, and stays quiet when everything is okay.  If it expects
    different output, IdioTest prints a diff.  If a program terminates
    abnormally, IdioTest prints the return code or the name of the
    signal which terminated the process.

  * Writing tests is easy.

  * You can hook instrumentation such as Valgrind into the programs
    you are testing.

How to write tests
------------------

You will need to write at least two files for your test suite: a
driver script and a test module.

The driver script is very simple, it imports IdioTest and calls a
function, passing in the path to the test modules and the path to find
executables.  Here is an example:

    #!/usr/bin/env python
    import idiotest
    import idiotest.run, sys, os
    idiotest.run.run(
        os.path.join(os.path.join(sys.path[0], 'tests')),
	['/path/bin']
    )

In this example, the test modules are located in the 'tests' directory
relative to the test driver script.  IdioTest will scan the test
directory for all files ending with '.py' and try to run them as
tests.  Modules are run in lexicographic order of pathname.

The test module can be very simple.  The following functions are
defined in all test modules:

test(...)
    Register a test.  Can be used as an ordinary function or as a
    decorator.  Tests must be callable.  As a decorator, it takes an
    optional argument specifying the test name.  As a function, it
    takes two parameters: a test name and the callable test object.
    See the example test module below.  Tests are run in the order in
    which they are registered.

fail(reason=None)
    Cause the current test to fail.

skip(reason=None)
    Cause the current test to be skipped.

fail_module(reason=None)
    Cause the entire module to fail and skip all tests in it.  May be
    called at any time in a test module.  Note that if this is called
    from the top level of a module, all tests will be skipped.

skip_module(reason=None)
    Casue all remaining tests in a module to be skipped, including the
    current one, if any.  May be called at any time in a test module.
    Note that if this is called from the top level of a module, all
    tests will be skipped.

get_output(cmd, input=None, cwd=None, result=0)
    Get the output from running a program.  Feeds the program 'input'
    as input, which is either a string or the name of a file prefixed
    with '@'.  Runs the program in the 'cwd' directory.  Causes the
    current test to fail if the exit status is anything other than
    'result'.

check_output(cmd, input=None, output=None, cwd=None, result=0)
    Get the output from running a program and check it against the
    expected output.  Behaves like get_output.  The 'output' argument
    is either a string or the name of a file prefixed with '@'.  If
    the program output differs form the expected output, check_output
    causes the current test to fail.

Example test
------------

Here is an example test module.  This is also part of the IdioTest
self-test, you can find it under 'selftest/demo.py'.

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

Command line usage
------------------

[test.py] [OPTIONS] [TESTS]

Specifying tests:

If TESTS is present, then it specifies a list of tests or modules to
run.

Module names are derived from their path relative to the test suite
root, and tests are given names based on their Python names or a name
explicitly specified with the 'test' function.  The components of
these names are joined with '.'.  For example, 'abc/test.py' is a
module named 'abc.test', and if it has a test named test_1, that test
has the full name 'abc.test.test_1'.

You can use wildcards when specifying tests.  For example, the
following invocation will run test_1, test_get_output, and
test_check_output in the demo above.  Note that test_2 is actually
named "Test #2", so it doesn't match.

    [test.py] 'demo.test_*'

You can run everything in the demo module by listing it by itself, for
example:

    [test.py] 'demo'

Other options:

-e, --err:  Send stderr to terminal.

    Normally, get_output and check_output will store the error output
    of the programs they run in memory.  The messages will only be
    printed if the program fails.  If this option is specified, stderr
    will always be sent directly to the terminal.

-w CMD, --wrap CMD:  Wrap commands with CMD.

    If this option is specified, all commands will be prefixed with
    CMD.  For example, you can run valgrind with full leak checking on
    your test suite with the following option:

        [test.py] --wrap='valgrind --leak-check=full'

--exec-path PATH:  Add PATH to the search path for executables.

    Paths added on the command line will take precedence over paths
    specified by the test script.


# IdioTest - idiotest/console.py
# Copyright 2009 Dietrich Epp <depp@zdome.net>
# This source code is licensed under the GNU General Public License,
# Version 3. See gpl-3.0.txt for details.
import sys
import idiotest.suite as suite

BOLD = 1

FG_RED = 31
FG_GREEN = 32
FG_YELLOW = 33
FG_BLUE = 34
FG_MAGENTA = 35
FG_CYAN = 36
FG_WHITE = 37

def hilite(string, *attr):
    """Add attributes to a string unless stdout is not a tty."""
    if not sys.stdout.isatty():
        return string
    attrs = ';'.join([str(a) for a in attr])
    return '\x1b[%sm%s\x1b[0m' % (attrs, string)

def box(width, string, *attr):
    """Format a string in a "box" (between square brackets)."""
    l = len(string)
    s = hilite(string, *attr)
    n = width - len(string)
    m = n // 2
    return '[%s%s%s]' % (' ' * (n - m), s, ' ' * m)

def show_reason(reason, indent=0):
    if not reason:
        return
    f = sys.stdout
    i = ' ' * indent
    for line in reason.splitlines():
        f.write(i)
        f.write(line)
        f.write('\n')
    f.write('\n')

def run_module(module, env, filter):
    """Run a test module, return test (success, fail, skip) counts."""
    if filter is not None and not filter.prefix_match(module.name):
        print '%s (skipped)' % module.name
        return 0, 0, 0
    status, data = module.load(env)
    if status == suite.FAIL:
        print '%-22s' % module.name, box(6, "FAILED", FG_RED, FG_BOLD)
        show_reason(data, 2)
        return 0, 1, 0
    elif status == suite.SKIP:
        print '%-22s' % module.name, box(6, "skip", FG_BLUE)
        show_reason(data, 2)
        return 0, 0, 1
    assert status == suite.SUCCESS
    tests = data
    if not tests:
        print '%s (no tests)' % module.name
        return 0, 0, 0
    numtest = len(tests)
    if filter is not None:
        tests = [t for t in tests
                 if filter.full_match(test.fullname)]
        numskip = numtest - len(tests)
        numtest = len(tests)
        print '%s (%d tests, skipping %d)' % \
            (module.name, numtest, numskip)
    else:
        numskip = 0
        print '%s (%d tests)' % (module.name, numtest)
    numsucc = 0
    numfail = 0
    with module.context():
        for test in tests:
            print '  %-20s' % test.name,
            sys.stdout.flush()
            status, reason = test.run()
            if status == suite.SUCCESS:
                if not test.fail:
                    numsucc += 1
                    print box(6, "ok", FG_GREEN)
                else:
                    numfail += 1
                    print box(6, "PASSED", FG_RED, BOLD), \
                        '(expected failure)'
            elif status == suite.FAIL:
                if not test.fail:
                    numfail += 1
                    print box(6, "FAILED", FG_RED, BOLD)
                else:
                    numsucc += 1
                    print box(6, "failed", FG_GREEN), '(expected)'
                show_reason(reason, 4)
            elif status == suite.SKIP:
                numskip += 1
                print box(6, "skip", FG_BLUE)
            else:
                assert False
    return numsucc, numfail, numskip

def run_suite(suite, env, filter):
    nummodule = len(suite.modules)
    failures = []
    numsucc = 0
    numfail = 0
    numskip = 0

    for module in suite.modules:
        msucc, mfail, mskip = run_module(module, env, filter)
        if mfail:
            failures.append((module, mfail))
        numsucc += msucc
        numfail += mfail
        numskip += mskip

    print
    print 'tests passed: %d' % (numsucc,)
    if numskip:
        print 'tests skipped: %d' % (numskip,)
    if numfail:
        print 'tests failed: %d' % (numfail,)
        for module, mfail in failures:
            print '  %s: %d failures' % (module.name, mfail)
        print 'test suite:', hilite('FAILED', FG_RED, BOLD)
        return False
    else:
        print 'test suite:', hilite('passed', FG_GREEN)
        return True

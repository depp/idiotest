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

def print_reason(reason, indent=0):
    if not reason:
        return
    f = sys.stdout
    i = ' ' * indent
    for line in reason.splitlines():
        f.write(i)
        f.write(line)
        f.write('\n')
    f.write('\n')

def const_true(x):
    return True

class ConsoleTest(object):
    def __init__(self, filter):
        self.module = None
        self.npass = 0
        self.nskip = 0
        self.nfail = 0
        self.failures = []
        self.partial_line = False
        if filter is not None:
            self.filter = f.prefix_match
        else:
            self.filter = const_true

    def clearline(self):
        if self.partial_line:
            print
            self.partial_line = False

    def module_begin(self, module):
        print module.name
        self.mpass = 0
        self.mskip = 0
        self.mfail = 0
        return self.filter(module.name)

    def module_end(self, module):
        if self.mfail:
            self.failures.append((module, self.mfail))
        self.npass += self.mpass
        self.nskip += self.mskip
        self.nfail += self.mfail
        del self.mpass
        del self.mskip
        del self.mfail
        print

    def module_pass(self, module):
        self.module_end(module)

    def module_fail(self, module, reason):
        self.mfail += 1
        self.clearline()
        print '    %s' % hilite('MODULE FAILED', FG_RED, BOLD)
        print_reason(reason, 4)
        self.module_end(module)

    def module_skip(self, module, reason):
        self.mskip += 1
        self.clearline()
        print '    %s' % hilite('module skipped', FG_BLUE)
        print_reason(reason, 4)
        self.module_end(module)

    def test_begin(self, test):
        print '  %-20s' % (test.name,),
        self.partial_line = True
        return self.filter(test.name)

    def test_pass(self, test):
        if not test.fail:
            print box(6, "ok", FG_GREEN)
            self.mpass += 1
        else:
            print box(6, "PASSED", FG_RED, BOLD), '(expected failure)'
            self.mfail += 1
        self.partial_line = False

    def test_fail(self, test, reason):
        if not test.fail:
            print box(6, 'FAILED', FG_RED, BOLD)
            self.mfail += 1
        else:
            print box(6, 'failed', FG_GREEN), '(as expected)'
            self.mpass += 1
        print_reason(reason, 4)
        self.partial_line = False

    def test_skip(self, test, reason):
        print box(6, 'skip', FG_BLUE)
        print_reason(reason, 4)
        self.mskip += 1
        self.partial_line = False

    def print_summary(self):
        print 'tests passed: %d' % (self.npass,)
        if self.nskip:
            print 'tests skipped: %d' % (self.nskip,)
        if self.nfail:
            print 'tests failed: %d' % (self.nfail,)
            for module, mfail in self.failures:
                print '  %s: %d failures' % (module.name, mfail)
            print 'test suite:', hilite('FAILED', FG_RED, BOLD)
        else:
            print 'test suite:', hilite('passed', FG_GREEN)

    def success(self):
        return self.nfail == 0

def run_suite(suite, env, filter):
    obj = ConsoleTest(filter)
    suite.run(obj, env)
    obj.print_summary()
    if obj.success():
        sys.exit(0)
    else:
        sys.exit(1)

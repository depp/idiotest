# IdioTest - idiotest/console.py
# Copyright 2009 Dietrich Epp <depp@zdome.net>
# This source code is licensed under the GNU General Public License,
# Version 3. See gpl-3.0.txt for details.
import traceback
import sys
import idiotest.fail

def hilite(string, status, bold):
    attr = []
    if status:
        # green
        attr.append('32')
    else:
        # red
        attr.append('31')
    if bold:
        attr.append('1')
    return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)

def run_tests(suite, filter):
    failed = '[%s]' % hilite("FAILED", False, True)
    ok = '[  %s  ]' % hilite("ok", True, False)
    scount = len(suite.names)
    failures = []
    atcount = 0
    ascount = 0
    for unitname in suite.names:
        if filter is not None and not filter.prefix_match(unitname):
            print '%s (skipped)' % unitname
            continue
        file = suite.files[unitname]
        file.load()
        if not file.names:
            print '%s (no tests)' % unitname
            continue
        if filter is not None:
            tests = []
            for testname in file.names:
                if filter.full_match('%s.%s' % (unitname, testname)):
                    tests.append(testname)
            tcount = len(tests)
            scount = 0
            print '%s (%i tests, skipping %i)' % (
                unitname, tcount, len(file.names) - tcount)
        else:
            tests = file.names
            tcount = len(tests)
            scount = 0
            print '%s (%i tests)' % (unitname, tcount)
        for testname in tests:
            test = file.tests[testname]
            print '  %-20s' % testname,
            sys.stdout.flush()
            try:
                test.run()
                result = True
            except idiotest.fail.TestFailure, ex:
                result = False
                reason = "%s\n%s" % (ex.reason, ex.msg.getvalue())
            except KeyboardInterrupt:
                raise
            except:
                result = False
                reason = traceback.format_exc()
            if result:
                print ok
                scount += 1
            else:
                print failed
                for line in reason.splitlines():
                    print '   ', line
                print
        if scount < tcount:
            failures.append((unitname, tcount, scount))
        atcount += tcount
        ascount += scount
    print
    print 'successes: %i/%i' % (ascount, atcount)
    if ascount < atcount:
        for unitname, tcount, scount in failures:
            print '  %s: %i/%i failures' % \
                (unitname, tcount - scount, tcount)
        print
        print 'test suite', failed
        sys.exit(1)
    else:
        print 'test suite', ok
        sys.exit(0)

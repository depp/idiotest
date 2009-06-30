#! /usr/bin/env python3.0
# IdioTest - test.py
# Copyright 2009 Dietrich Epp <depp@zdome.net>
# This source code is licensed under the GNU General Public License,
# Version 3. See gpl-3.0.txt for details.

# HOW TO WRITE A TEST

# Just make a python script in a subdirectory.  Write a bunch of
# functions in that script with "test" somewhere in the name.  Call
# fail(reason) whenever you fail, throwing an exception works too.
# You can access files, the cwd will be the directory your foo.py is
# in.  You can call check_output() as well.

import optparse
import os
import sys
import traceback
import subprocess
import difflib
import io

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

class TestFailure(Exception):
    def __init__(self, reason):
        self.reason = reason

def fail(reason=None):
    raise TestFailure(reason)

def runproc(*args, stdin=None, **kw):
    proc = subprocess.Popen(stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            *args, **kw)
    out, err = proc.communicate(stdin)
    return out, err, proc.returncode

def getsigdict():
    import signal
    d = {}
    for k, v in signal.__dict__.items():
        if k.startswith('SIG') and isinstance(v, int):
            d[v] = k
    return d
sigdict = getsigdict()
def signame(signum):
    try:
        name = sigdict[signum]
    except KeyError:
        return 'signal %i' % (signum,)
    return 'signal %i (%s)' % (signum, name)

def check_output(cmd, input, output):
    """Check the output of an external command.

    check_output(cmd, input, output)

    This will run cmd, feed it input, and check that the output
    matches the expected output.  If it doesn't, fail() will be called
    with a bunch of helpful diagnostics including the program's stderr
    output and the diff between the expected and actual output.
    """
    if isinstance(input, str):
        input = input.encode('utf8')
    if isinstance(output, str):
        output = output.encode('utf8')
    out, err, retcode = runproc(cmd, stdin=input)
    if retcode != 0:
        reason = io.StringIO()
        if retcode < 0:
            print('program received %s' % (signame(-retcode),), file=reason)
        else:
            print('program returned %i' % (retcode,), file=reason)
        print('command: %r' % (cmd,), file=reason)
        if out:
            print('=== OUTPUT ===', file=reason)
            try:
                out = out.decode('utf8')
                for line in out.splitlines():
                    print('  ' + line, file=reason)
            except UnicodeDecodeError:
                print('<invalid unicode>', file=reason)
                for line in out.splitlines():
                    print('  ' + repr(line), file=reason)
    elif output is not None and out != output:
        reason = io.StringIO()
        print('incorrect output', file=reason)
        print('command: %r' % (cmd,), file=reason)
        print('=== DIFF ===', file=reason)
        output = output.decode('utf8').splitlines(True)
        try:
            out = out.decode('utf8').splitlines(True)
            diff = difflib.Differ().compare(output, out)
            for line in diff:
                reason.write(line)
        except UnicodeDecodeError:
            print('<invalid unicode>', file=reason)
            for line in out.splitlines():
                print('  ' + repr(line), file=reason)
    else:
        return
    if err:
        print('=== ERROR ===', file=reason)
        try:
            err = err.decode('utf8')
            for line in err.splitlines():
                print('  ' + line, file=reason)
        except UnicodeDecodeError:
            print('<invalid unicode>', file=reason)
    fail(reason.getvalue())

FAILED = hilite("FAILED", False, True)
OK = hilite("  ok  ", True, False)

def run_test(name, test):
    sys.stdout.write("  %-20s" % name)
    sys.stdout.flush()
    try:
        test()
        result = True
    except TestFailure as ex:
        result = False
        reason = ex.reason + '\n'
    except:
        result = False
        reason = traceback.format_exc()
    if result:
        sys.stdout.write(' [%s]\n' % (OK,))
        return True
    sys.stdout.write(' [%s]\n' % (FAILED,))
    for line in reason.splitlines():
        sys.stdout.write('    %s\n' % (line,))
    return False

def run():
    parser = optparse.OptionParser()
    parser.add_option('--self-test', action="store_true", dest="self_test",
                      default=False, help="run test of testing framework")
    (options, args) = parser.parse_args()
    if args:
        print("Arguments not understood.", file=sys.stderr)
        sys.exit(1)
    if not options.self_test:
        testfiles = set()
        for dirpath, dirnames, filenames in os.walk('.'):
            dirnames[:] = [dirname for dirname in dirnames
                           if not dirname.startswith('.')
                           and dirname != 'selftest']
            if dirpath == '.':
                continue
            for filename in filenames:
                if not filename.endswith('.py'):
                    continue
                if filename.startswith('.'):
                    continue
                path = os.path.normpath(os.path.join(dirpath, filename))
                testfiles.add(path)
    else:
        testfiles = ['selftest/selftest.py']
    pkg_globals = {
        'fail': fail,
        'check_output': check_output,
    }
    acount = 0
    atcount = 0
    ascount = 0
    fsuites = []
    originalwd = os.getcwd()
    for path in testfiles:
        g = dict(pkg_globals)
        inf = open(path, 'rb')
        text = inf.read()
        inf.close()
        os.chdir(os.path.dirname(path))
        exec(text, g)
        tests = []
        if 'tests' in g:
            for t in g['tests']:
                for k, v in g.items():
                    if v is t:
                        name = k
                        break
                else:
                    try:
                        name = t.__name__
                    except:
                        name = repr(t)
                tests.append((name, t))
        else:
            for k, v in sorted(g.items()):
                if 'test' in k.lower() and hasattr(v, '__call__'):
                    tests.append((k, v))
            tests.sort()
        if not tests:
            print('%s (no tests)' % (path,))
        else:
            tcount = len(tests)
            scount = 0
            print('%s (%i)' % (path, tcount))
            for k, v in tests:
                if run_test(k, v):
                    scount += 1
            acount += 1
            atcount += tcount
            ascount += scount
            if ascount < atcount:
                fsuites.append((path, tcount - scount))
        os.chdir(originalwd)
    print()
    print('successes: %i/%i' % (ascount, atcount))
    if ascount < atcount:
        print('failures: %i/%i in %i suites:' %
              (atcount - ascount, atcount, len(fsuites)))
        for (suite, failures) in fsuites:
            print('  %s [%s] %i failures' %
                  (suite, FAILED, failures))
        print()
        print('[%s]' % (FAILED,))
        sys.exit(1)
    else:
        print('[%s]' % (OK,))
        sys.exit(0)
run()

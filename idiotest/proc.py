# IdioTest - idiotest/proc.py
# Copyright 2009 Dietrich Epp <depp@zdome.net>
# This source code is licensed under the GNU General Public License,
# Version 3. See gpl-3.0.txt for details.
"""IdioTest process utilities.

This contains the TestProc class, which runs a program and compares
its output to the expected output.  It is fairly versatile.
"""
import subprocess
from cStringIO import StringIO
import encodings.utf_8
import idiotest.fail
import difflib

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

class ProcException(idiotest.fail.TestFailure):
    pass
class ProcFailure(ProcException):
    def __init__(self, retval):
        ProcException.__init__(self, u"process returned failure (%i)" % retval)
        self.retval = retval
class ProcSignal(ProcException):
    def __init__(self, signal):
        ProcException.__init__(self, u"process received %s" % signame(signal))
        self.signal = signal
class ProcOutput(ProcException):
    def __init__(self):
        ProcException.__init__(self, u"incorrect output")

def write_stream(name, stream, file):
    if not stream:
        return
    file.write(u"=== %s ===\n" % name)
    try:
        if not isinstance(stream, unicode):
            stream = encodings.utf_8.decode(stream)[0]
    except UnicodeDecodeError:
        file.write(u'<invalid unicode>\n')
        for line in stream.splitlines():
            file.write(u'  %s\n' % repr(line)[1:-1])
        if stream and not stream.endswith('\n'):
            file.write(u'<no newline at end of stream>\n')
    else:
        for line in stream.splitlines():
            file.write(u'  %s\n' % line)
        if stream and not stream.endswith(u'\n'):
            file.write(u'<no newline at end of stream>\n')

class InNone(object):
    def popenarg(self):
        return subprocess.PIPE
    def commarg(self):
        return ''
    def __nonzero__(self):
        return False
    def decorate(self, err):
        pass
class InFile(object):
    def __init__(self, path):
        self.path = path
    def popenarg(self):
        return open(self.path, 'rb')
    def commarg(self):
        return None
    def decorate(self, err):
        err.write(u"input file: %s\n" % repr(self.path))
    def contents(self):
        return open(self.path, 'rb').read()
class InString(object):
    def __init__(self, string):
        self.string = string
    def popenarg(self):
        return subprocess.PIPE
    def commarg(self):
        if isinstance(self.string, unicode):
            return encodings.utf_8.encode(self.string)[0]
        return self.string
    def decorate(self, err):
        write_stream(u'stdin', self.string, err)
    def contents(self):
        return self.string

def parse_input(input):
    if input is None:
        return InNone()
    if input.startswith('@'):
        return InFile(input[1:])
    return InString(input)

class Proc(object):
    def __init__(self, cmd, input, cwd, geterr):
        self.cmd = cmd
        self.input = input
        self.cwd = cwd
        self.error = None
        self.output = None
        self.geterr = geterr
    def run(self):
        if self.geterr:
            stderr = subprocess.PIPE
        else:
            stderr = None
        proc = subprocess.Popen(
            self.cmd, cwd=self.cwd, stdin=self.input.popenarg(),
            stdout=subprocess.PIPE, stderr=stderr)
        output, error = proc.communicate(self.input.commarg())
        retcode = proc.returncode
        self.output = output
        self.error = error
        self.retcode = retcode
    def check_signal(self):
        if self.retcode < 0:
            err = ProcSignal(-self.retcode)
            self.decorate(err)
            raise err
    def check_success(self, result):
        self.check_signal()
        if self.retcode != result:
            err = ProcFailure(self.retcode)
            self.decorate(err)
            raise err
    def decorate(self, err):
        err.write(u'command: %s\n' % ' '.join(self.cmd))
        if self.cwd is not None:
            err.write(u'cwd: %s\n' % self.cwd)
        self.input.decorate(err)
        write_stream('stderr', self.error, err)

class ProcRunner(object):
    def __init__(self):
        self.geterr = True
    def proc(self, cmd, input, cwd):
        return Proc(cmd, input, cwd, self.geterr)
    def get_output(self, cmd, input=None, cwd=None, result=0):
        p = self.proc(cmd, parse_input(input), cwd)
        p.run()
        p.check_success(result)
        return p.output
    def check_output(self, cmd, input=None, output=None,
                     cwd=None, result=0):
        p = self.proc(cmd, parse_input(input), cwd)
        p.run()
        p.check_success(result)
        output = parse_input(output).contents()
        procout = p.output
        if isinstance(output, unicode):
            try:
                procout = encodings.utf_8.decode(procout)[0]
            except UnicodeDecodeError:
                err = ProcOutput()
                p.decorate(err)
                write_stream(u'output', procout, err)
                raise err
            if procout != output:
                err = ProcOutput()
                p.decorate(err)
                eout = output.splitlines(True)
                pout = procout.splitlines(True)
                err.write(u"=== diff ===\n")
                for line in difflib.Differ().compare(eout, pout):
                    err.write(line)
                raise err
        else:
            if procout != output:
                err = ProcOutput()
                p.decorate(err)
                eout = [repr(x)+'\n' for x in output.splitlines(True)]
                pout = [repr(x)+'\n' for x in procout.splitlines(True)]
                err.write(u"=== diff ===\n")
                for line in difflib.Differ().compare(eout, pout):
                    err.write(line)
                raise err

class ProcWrapper(ProcRunner):
    def __init__(self, wrap):
        ProcRunner.__init__(self)
        cmd = wrap.split()
        for n, part in enumerate(cmd):
            if part == '%':
                self.prefix = cmd[:n]
                self.suffix = cmd[n+1:]
                break
        else:
            raise Exception("Invalid wrapper, missing %%: %s" % repr(wrap))
    def proc(self, cmd, input, cwd):
        cmd2 = self.prefix + cmd + self.suffix
        return ProcRunner.proc(self, cmd2, input, cwd)

# Copyright 2009, 2012 Dietrich Epp <depp@zdome.net>
# See LICENSE.txt for details.
"""IdioTest process utilities.

This contains the TestProc class, which runs a program and compares
its output to the expected output.  It is fairly versatile.
"""
from __future__ import absolute_import
import subprocess
from cStringIO import StringIO
import encodings.utf_8
import idiotest.exception
import difflib
import errno
import os.path

TestFailure = idiotest.exception.TestFailure

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

class ProcException(TestFailure):
    pass
class ProcNotFound(ProcException):
    def __init__(self, name):
        ProcException.__init__(self, u"executable not found: %r" % name);
        self.name = name
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
class ProcPipe(ProcException):
    def __init__(self):
        ProcException.__init__(self, u"process closed stdin unexpectedly")
        self.retval = -1

def write_stream(name, stream, file):
    if not stream:
        return
    file.write(u"=== %s ===\n" % name)
    ustream = None
    if '\x00' not in stream:
        try:
            if not isinstance(stream, unicode):
                ustream = encodings.utf_8.decode(stream)[0]
        except UnicodeDecodeError:
            pass
    if ustream is None:
        file.write(u'<binary>\n')
        for line in stream.splitlines():
            file.write(u'  %s\n' % repr(line)[1:-1])
        if stream and not stream.endswith('\n'):
            file.write(u'<no newline at end of stream>\n')
    else:
        for line in ustream.splitlines():
            file.write(u'  %s\n' % line)
        if ustream and not ustream.endswith(u'\n'):
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
    """A Proc object represents a process that can be run.

    It is essentially a wrapper around a subprocess.Popen object.
    """

    def __init__(self, cmd, executable=None, input=None,
                 cwd=None, geterr=None):
        self.cmd = cmd
        self.executable = executable
        self.input = input
        self.cwd = cwd
        self.error = None
        self.output = None
        self.geterr = geterr
        self.broken_pipe = False

    def run(self):
        """Run the process."""
        if self.geterr:
            stderr = subprocess.PIPE
        else:
            stderr = None
        proc = subprocess.Popen(
            self.cmd, executable=self.executable,
            cwd=self.cwd, stdin=self.input.popenarg(),
            stdout=subprocess.PIPE, stderr=stderr)
        try:
            output, error = proc.communicate(self.input.commarg())
        except OSError, ex:
            if ex.errno == errno.EPIPE:
                self.broken_pipe = True
                proc.wait()
                output = ''
                error = ''
            else:
                raise
        retcode = proc.returncode
        self.output = output
        self.error = error
        self.retcode = retcode

    def check_signal(self):
        """Raise an exception if the process was terminated by a signal."""
        if self.retcode < 0:
            err = ProcSignal(-self.retcode)
            self.decorate(err)
            raise err

    def check_success(self, result):
        """Raise an exception if the process gave an incorrect status."""
        self.check_signal()
        if self.retcode != result:
            err = ProcFailure(self.retcode)
            self.decorate(err)
            raise err
        if self.broken_pipe:
            err = ProcPipe()
            self.decorate(err)
            raise err

    def decorate(self, err):
        """Add process information to an exception."""
        err.write(u'command: %s\n' % ' '.join(self.cmd))
        if self.cwd is not None:
            err.write(u'cwd: %s\n' % self.cwd)
        self.input.decorate(err)
        write_stream('stderr', self.error, err)

class ProcRunner(object):
    """A ProcRunner runs programs for a test suite.

    It searches for program executables and modifies program arguments
    if necessary.
    """
    ENV = ['check_output', 'get_output']
    def __init__(self, options):
        self.geterr = not options.err
        self.paths = [os.path.abspath(path) for path in options.exec_paths]
        try:
            ospaths = os.environ['PATH']
        except KeyError:
            pass
        else:
            for ospath in ospaths.split(os.pathsep):
                if not ospath:
                    continue
                self.paths.append(os.path.abspath(ospath))
        self.path_cache = {}

    def find_executable(self, name):
        """Find an executable in the search path.

        If the program name starts with '.', '..', or '/', then it is
        returned directly.  Otherwise, it is appended to each search
        path until a file is found.  If no file is found, ProcNotFound
        is raised.
        """
        try:
            return self.path_cache[name]
        except KeyError:
            pass
        if name.startswith('./') or name.startswith('../') \
                or name.startswith('/'):
            return name
        for path in self.paths:
            path = os.path.normpath(os.path.join(path, name))
            if os.path.isfile(path):
                self.path_cache[name] = path
                return path
        raise ProcNotFound(name)

    def proc(self, cmd, input, cwd):
        """Get the Proc object to run the command."""
        executable = self.find_executable(cmd[0])
        return Proc(cmd, executable=executable, input=input,
                    cwd=cwd, geterr=self.geterr)

    def get_output(self, cmd, input=None, cwd=None, result=0):
        """Run a program and return the output."""
        p = self.proc(cmd, parse_input(input), cwd)
        p.run()
        p.check_success(result)
        return p.output

    def check_output(self, cmd, input=None, output=None,
                     cwd=None, result=0):
        """Run a program and check the output against a reference."""
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
    def __init__(self, options):
        ProcRunner.__init__(self, options)
        self.wrap = options.wrap.split()
    def proc(self, cmd, input, cwd):
        proc = ProcRunner.proc(self, cmd, input, cwd)
        proc.cmd = self.wrap + proc.cmd
        return proc

def env(options):
    if options.wrap:
        return ProcWrapper(options)
    else:
        return ProcRunner(options)

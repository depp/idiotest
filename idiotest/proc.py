# Copyright 2009, 2012 Dietrich Epp <depp@zdome.net>
# See LICENSE.txt for details.
"""IdioTest process utilities.

This contains the TestProc class, which runs a program and compares
its output to the expected output.  It is fairly versatile.
"""
from __future__ import absolute_import
import subprocess
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

class ProcFailure(TestFailure):
    pass
class ProcNotFound(ProcFailure):
    def __init__(self, name):
        ProcFailure.__init__(self, u"executable not found: %r" % name);
        self.name = name
class ProcStatusError(ProcFailure):
    def __init__(self, retval):
        ProcFailure.__init__(self, u"process returned failure (%i)" % retval)
        self.retval = retval
class ProcSignalError(ProcFailure):
    def __init__(self, signal):
        ProcFailure.__init__(self, u"process received %s" % signame(signal))
        self.signal = signal
class ProcOutputError(ProcFailure):
    def __init__(self):
        ProcFailure.__init__(self, u"incorrect output")
class ProcBrokenPipe(ProcFailure):
    def __init__(self):
        ProcFailure.__init__(self, u"process closed stdin unexpectedly")

def write_stream(name, stream, file):
    if not stream:
        return
    file.write(u"=== %s ===\n" % name)
    ustream = None
    if '\x00' not in stream:
        try:
            if not isinstance(stream, unicode):
                ustream = stream.decode('UTF-8')
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

class Proc(object):
    """A Proc object represents a process that can be run.

    It is essentially a wrapper around a subprocess.Popen object.  It
    is somewhat simplified.  For example, it accepts strings or files
    for input, and does not expose pipe functionality.  If you need
    fancy pipes, you can always call subprocess.Popen yourself.
    """

    def __init__(self, args,
                 executable=None, input=None, cwd=None, geterror=False):
        self.args = list(args)
        self.executable = executable
        self.input = input
        self.cwd = cwd
        self.geterror = geterror
        self.broken_pipe = False

    def run(self):
        """Run the process."""
        stderr = subprocess.PIPE if self.geterror else None
        stdin = self.input
        if isinstance(stdin, basestring):
            if isinstance(stdin, unicode):
                carg = stdin.encode('UTF-8')
            elif isinstance(stdin, str):
                carg = stdin
            else:
                raise TypeError('input should be string, file, or None')
            stdin = subprocess.PIPE
        elif hasattr(stdin, 'read'):
            carg = None
        elif stdin is None:
            stdin = subprocess.PIPE
            carg = None
        else:
            raise TypeError('input must be file, string, or None')
        proc = subprocess.Popen(
            self.args, executable=self.executable, cwd=self.cwd,
            stdin=stdin, stdout=subprocess.PIPE, stderr=stderr,
            close_fds=True)
        try:
            output, error = proc.communicate(carg)
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

    def check_exit(self, status):
        """Raise an exception if the process exited incorrectly.

        The status should either be an integer, a callable object
        which returns True for a correct status and False for an
        incorrect status, or None.  If None, then any status is
        acceptable and only signals are considered errors.
        """
        code = self.retcode
        if code < 0:
            err = ProcSignalError(-code)
            self.decorate(err)
            raise err
        if callable(status):
            error = not status(code)
        elif status is None:
            error = False
        else:
            error = status != code
        if error:
            err = ProcStatusError(code)
            self.decorate(err)
            raise err
        if self.broken_pipe:
            err = ProcBrokenPipe()
            self.decorate(err)
            raise err

    def decorate(self, err):
        """Add process information to an exception."""
        err.write(u'command: %s\n' % ' '.join(self.args))
        if self.cwd is not None:
            err.write(u'cwd: %s\n' % self.cwd)
        stdin = self.input
        if isinstance(stdin, basestring):
            write_stream(u'stdin', stdin, err)
        elif hasattr(stdin, 'read'):
            err.write(u"input file: %s\n" % repr(stdin.name))
        elif stdin is None:
            pass
        else:
            raise TypeError('input must be file, string, or None')
        write_stream('stderr', self.error, err)

    def check_output(self, output=None):
        """Raise an exception if the program gave incorrect output.

        The expected output can be a file, string, unicode object, or
        None.  If None, no output is expected.  If a byte string, then
        the output is compared to the string.  If a unicode string,
        the output is decoded as UTF-8 and compared to the string.  If
        a file, the file contents are compared against the output.
        """
        try:
            procout = self.output
        except AttributeError:
            raise Exception('program has not been run')
        if isinstance(output, basestring):
            outstr = output
        elif hasattr(output, 'read'):
            outstr = output.read()
        elif output is None:
            outstr = ''
        else:
            raise TypeError('output must be file, string, or None')
        if isinstance(outstr, unicode):
            try:
                procout = procout.decode('UTF-8')
            except UnicodeDecodeError:
                err = ProcOutputError()
                p.decorate(err)
                write_stream(u'output', procout, err)
                raise err
            if procout != outstr:
                err = ProcOutputError()
                p.decorate(err)
                eout = outstr.splitlines(True)
                pout = procout.splitlines(True)
                err.write(u"=== diff ===\n")
                for line in difflib.Differ().compare(eout, pout):
                    err.write(line)
                raise err
        elif isinstance(outstr, str):
            if procout != outstr:
                err = ProcOutputError()
                self.decorate(err)
                eout = [repr(x)+'\n' for x in outstr.splitlines(True)]
                pout = [repr(x)+'\n' for x in procout.splitlines(True)]
                err.write(u"=== diff ===\n")
                for line in difflib.Differ().compare(eout, pout):
                    err.write(line)
                raise err
        else:
            raise TypeError('output must yield a string or unicode object')

class ProcRunner(object):
    """A ProcRunner runs programs for a test suite.

    It searches for program executables and modifies program arguments
    if necessary.
    """

    def __init__(self, options):
        self.geterror = not options.err
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
        if options.wrap:
            wrap = options.wrap.split()
            if not wrap:
                raise Exception('--wrap cannot be empty')
            try:
                self.executable = self.find_executable(wrap[0])
            except ProcNotFound:
                raise Exception('--wrap: program not found: %r' % wrap[0])
            self.wrap = wrap
        else:
            self.wrap = None

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

    def proc(self, args, executable=None, geterror=False, **kw):
        """Create a Proc object for running a program.

        Raises an exception if the program is not found.
        """
        if executable is None:
            executable = self.find_executable(args[0])
        if self.wrap is not None:
            args = self.wrap + [executable] + args[1:]
            executable = self.executable
        geterror = geterror or self.geterror
        return Proc(args, executable=executable, geterror=geterror, **kw)

    def run(self, args, status=0, **kw):
        """Run a program and return the Proc object.

        Raises an exception if the program is not found, if the
        timeout expires, if the program is terminated by a signal, if
        the process does not consume its input, or if the program
        returns an invalid status code.  The status code will not be
        checked if status is None.
        """
        proc = self.proc(args, **kw)
        proc.run()
        proc.check_exit(status)
        return proc

    def get_output(self, args, **kw):
        """Run a program and return its output.

        Fails under the same conditions as 'run'.
        """
        return self.run(args, **kw).output

    def check_output(self, args, output=None, **kw):
        """Run a program and check its output against a reference.

        Fails under the same conditions as 'run'.  Raises an exception
        if the program output does not match the reference output.
        """
        self.run(args, **kw).check_output(output)

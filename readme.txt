IdioTest: A stupid testing framework
====================================
Dietrich Epp

IdioTest is a simple and stupid testing framework.  Tests in IdioTest
run programs, feed those programs input, and compare the output to the
expected output.  IdioTest does not know or care what language you
write your programs in.  Tests in IdioTest are written in Python.

IdioTest is incomplete, I am still writing it.  I am putting it in its
own project and documenting it because I had copies of it in three
different projects, out of synch with each other.  Here are the goals:

- No hooks into the development environment.  Tests just run programs
  and check the output.  No additional libraries or definitions need
  to be added to the programs.
- Tests are clean.  Each runs in its own process, free to assert() for
  failure or even segfault.
- Writing tests is easy.
- The output of the test suite is easy to visually scan.
- Failed tests give an appropriate amount of information: signal
  names, return codes, standard error, and diffs between the actual
  and expected output.

Future ideas:

- It should be possible to hook instrumentation into the tests, such
  as memory tools (e.g. Valgrind), coverage tests, debuggers, and
  profilers.

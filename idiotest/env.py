# Copyright 2009, 2012 Dietrich Epp <depp@zdome.net>
# See LICENSE.txt for details.
"""IdioTest global environment for test modules."""
from __future__ import absolute_import
import idiotest.proc
import idiotest.exception

def add_env(env, module):
    for var in module.ENV:
        env[var] = getattr(module, var)

def make_env(options):
    """Make an execution environment with the given command line options."""
    env = dict()
    add_env(env, idiotest.exception)
    env['proc'] = idiotest.proc.ProcRunner(options)
    return env

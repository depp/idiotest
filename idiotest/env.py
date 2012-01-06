"""IdioTest global environment for test modules."""
import idiotest.proc
import idiotest.exception

def add_env(env, module):
    for var in module.ENV:
        env[var] = getattr(module, var)

def make_env(options):
    """Make an execution environment with the given command line options."""
    env = dict()
    add_env(env, idiotest.exception)
    add_env(env, idiotest.proc.env(options))
    return env

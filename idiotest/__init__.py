__all__ = ['run']
import idiotest.suite

def run(root='.'):
    suite = idiotest.suite.TestSuite(root)
    for test in suite.testnames:
        print(test)

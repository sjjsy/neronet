# dmntest.py

from .core import Daemon

class TestDmn(Daemon):
    pass

if __name__ == '__main__':
    td = TestDmn('testd')
    td.start()
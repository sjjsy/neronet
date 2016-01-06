# nerodmn.py

import nerodmnc

class TestDmn(nerodmnc.DaemonA):
    pass

def main():
    td = TestDmn('testd')
    td.start()
    td.query('test', foo='bar')
    td.terminate()
# nerodmn.py

import sys
import nerodmnc

class TestDmn(nerodmnc.DaemonA):
    pass

def main():
    td = TestDmn('testd')
    arg = sys.argv[1]
    if arg == 'start': td.start()
    elif arg == 'stop': td.stop()
    elif arg == 'restart': td.restart()
    elif arg == 'status':
        data = td.query('status')['kwargs']
        print('Received a reply (code %d):' % (data['rv']))
        print(data['msgbody'])
    elif arg == 'test': td.query('test', foo='bar')

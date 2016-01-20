from __future__ import print_function
import os
import sys

def main():
    defaultfile = 'simple_sys_test_cmds.txt'
    #A hack to make it work in python3
    try:
        _input = raw_input
    except NameError:
        _input = input

    try:
        f = sys.argv[1]
    except IndexError:
        f = defaultfile
    with open(f, 'r') as file:
        for line in file:
            _input('Press Enter to execute next line:\n %s' % line)
            os.system(line)

if __name__ == '__main__':
    main()

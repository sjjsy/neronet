# main.py
#
# Usage: main.py n breaktime
# Examples:
#   main.py 100 1
#   main.py 100 0.01
#
# Computes the <n>th fibonacci number writing all intermediate numbers along
# with seconds since start while sleeping <breaktime> seconds at each step.
#
# The value of n must be at least 3.

import sys
import time

n = int(sys.argv[1])
breaktime = float(sys.argv[2])
if n < 3:
    print('N must be >= 3!')
    sys.exit(1)
starttime = time.time()
a = b = 1
print('time\tindex\tvalue')
for i in range(3, n+1):
    a, b = a + b, a
    time.sleep(breaktime)
    print('%d\t%d\t%d' % (time.time() - starttime, i, a))
    sys.stdout.flush()
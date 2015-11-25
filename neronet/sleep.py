# sleep.py
#
# Usage: sleep.py count interval
# Examples:
#   sleep.py 4 10
#   sleep.py 100 0.4
#
# Writes the system time <count> times into stdout with an interval of
# <interval> seconds

import sys
import time
import datetime

count = int(sys.argv[1])
interval = float(sys.argv[2])

for i in range(1, count+1):
    time.sleep(interval)
    print('%s: %d/%d (%.1f)' % (datetime.datetime.now(), i, count, interval))
    sys.stdout.flush()

# testexp.py
#
# Usage: testexp.py count interval
# Example: testexp.py 100 10
#
# Writes the system time <count> times into stdout with an interval of
# <interval> seconds

import sys
import datetime

arguments = sys.argv
count = int(arguments[1])
interval = int(arguments[2])
for i in range(count):
  sys.sleep(interval)
  print(datetime.now())
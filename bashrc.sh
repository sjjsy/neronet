#!/bin/bash
if [ -n "$VIRTUAL_ENV" ]; then deactivate; fi
source venv27/bin/activate
export PYTHONPATH="$PWD:/usr/lib/python2.7/dist-packages"
export PATH="$PWD/bin:$PATH"

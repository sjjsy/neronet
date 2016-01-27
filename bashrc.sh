#!/bin/bash
if [ -n "$VIRTUAL_ENV" ]; then deactivate; fi
source venv27/bin/activate
export PYTHONPATH="$PWD"
export PATH="$PWD/bin:$PATH"

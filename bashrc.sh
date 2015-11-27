#!/bin/bash
if [ -n "$VIRTUAL_ENV" ]; then deactivate; fi
source venv/bin/activate
export PYTHONPATH="$PWD"
export PATH="$PWD/bin:$PATH"

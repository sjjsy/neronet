#!/bin/bash
venv=${1-venv27}
if [ -n "$VIRTUAL_ENV" ]; then deactivate; fi
source "$venv/bin/activate"
export PYTHONPATH="$PWD:/usr/lib/python2.7/dist-packages"
export PATH="$PWD/bin:$PATH"
function neroclean(){
  echo "Cleaning localhost..."
  nerocli --clean
  echo "Cleaning kosh..."
  ssh kosh.aalto.fi 'rm -r ~/.neronet'
}

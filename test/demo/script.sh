#!/bin/bash
# script.sh
nerocli --addnode kosh unmanaged akosh
nerocli --addnode brute unmanaged abrute
nerocli --addnode mozart unmanaged amozart
nerocli --addnode mahler unmanaged amahler
nerocli --addnode thoth unmanaged athoth

nerocli --addexp test/experiments/fibonacci
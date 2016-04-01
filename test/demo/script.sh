#!/bin/bash
# script.sh
nerocli --addnode kosh akosh
nerocli --addnode mozart amozart
nerocli --addnode mahler amahler
nerocli --addnode thoth athoth
nerocli --addexp test/experiments/sleep
nerocli --addexp test/experiments/fibonacci
nerocli --addexp test/experiments/fileio

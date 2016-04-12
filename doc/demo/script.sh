#!/bin/bash
# This bash script demonstrates Neronet's CLI functionality.

# Install neronet
pip install neronet

# Check SSH configuration to ensure your nodes are setup with SSH
vim ~/.ssh/config
ls -l ~/.ssh/*rsa

# Add nodes (on my SSH setup Aalto nodes are named with a prepended)
nerocli --addnode kosh akosh
nerocli --addnode mozart amozart
nerocli --addnode mahler amahler
nerocli --addnode thoth athoth

# Ensure experiments are correctly defined
ls -l ./experiments/*
vim -p ./experiments/*.config

# Add the experiments
nerocli --addexp ./experiments/fibonacci
nerocli --addexp ./experiments/fileio

# Ensure Neronet became aware of your setup
nerocli --status

# Check the status of your nodes
nerocli --status nodes

# Inspect experiment info
nerocli --status fibonacci_breaktime-0.1_n-1000

# Submit three experiments to two nodes for computation
nerocli --submit fibonacci_breaktime-0.1_n-100 mozart
nerocli --submit fibonacci_breaktime-0.1_n-1000 mahler
nerocli --submit fileio2 mahler

# Check overall status
nerocli --status

# Fetch an info update from the node and check experiment status again
nerocli --fetch
nerocli --status fibonacci_breaktime-0.1_n-100
nerocli --status fibonacci_breaktime-0.1_n-1000

# Check mid-computation data
ls -l ~/.neronet/experiments/fibonacci_breaktime-0.1_n-1000/

# Fetch another info update from the node and check experiment status
nerocli --fetch
nerocli --status fibonacci_breaktime-0.1_n-100
nerocli --status fibonacci_breaktime-0.1_n-1000

# Check overall status
nerocli --status

# Check post-computation (final) data
ls -l ./experiments/*/results/*/

# Thank you!
echo "Hope you got an idea of what Neronet can do for you!"

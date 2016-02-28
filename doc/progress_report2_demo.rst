Progress report 2 demo script
=============================

CLI
---

#. Installation: pip install neronet
#. Setup kosh at SSH config: vim ~/.ssh/config
#. Cluster conf: nerocli --cluster kosh unmanaged aalto
#. Experiment conf: vim experiments/sleep/config
#. Experiment conf: nerocli --experiment experiments/sleep
#. Check status: nerocli --status
#. Check status: nerocli --status sleep1
#. Submit experiment: nerocli --submit sleep1 kosh
#. Fetch information: nerocli --fetch
#. Check status: nerocli --status sleep1
#. Repeat last two steps until finished
#. Check status: nerocli --plot

GUI
---

Notes:
- Remember to say *toot* everytime you press buttons

1. Add experiment by pressing "add experiment" and by navigating to test/experiments and select theanotest and press open.
2. Do the same for sleep.
3. Press any xperiment and say that we can see detailed information of the last selected experiment on rightmost field.
4. Select another experiment and point that we can easily compare parameters of different experiments.
5. select theano experiment and any sleep experiment and point how we can compare experiments with different parameters.
6. Add cluster by typing the info and prssing "add cluster"
7. Submit any experiment(s) by selecting clusters and experimentsand press submit.
8. Press refresh to fetch pending results
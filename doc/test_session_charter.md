Test Session Charter

# 1. What - tested areas

GUI and CLI:

- Installation
- Cluster specification
- Experiment specification, submitting, result fetching.

# 2. Why - goal and focus

The first purpose of our testing is to see if a technically proficient user
is able to start using our program with the help of the current start guide,
without needing any other guidance. Another potential benefit of the testing
is discovering potential errors in important functions such as cluster
specification, experiment specification and experiment submission.

In addition to testing Neronet using the CLI, we will also test the GUI to
confirm that it can also be used to perform the most important functions.

# 3. How - approach

For the testing session we will meet at Maarintalo, in the class 240/241. To
test Neronet, we will use a UNIX system which can be a personal laptop or
simply a public access desktop at Maari. We will set up a virtualenv so that
the installation doesn't conflict with other Python packages on the computer.
After this we instruct the testers to try and install and use Neronet as a
normal user would.

Testing data to be used is simply the example experiments we have prepared.

# 4. Exploration log

To be filled!

- SESSION START TIME: 13:00
- DURATION (hours): 4h
- TESTER: Kaarlo, Olli, Joni
- BUILD: 0.3.1
- ENVIRONMENT: Teemu's and Tuomo's Linux laptops

## 4.1 Data files

- test/experiments/sleep
- test/experiments/sleep001
- test/experiments/theanotest

## 4.2 Test notes

- Test notes that describe what was done, and how.
- Detailed enough to be able to use in briefing the test session with other
  persons.
- Detailed enough to be able to reproduce failures.

## 4.3 Bugs

Defect tracking system bug ID:s and optionally short descriptions

## 4.4 Issues

Any observations, issues, new feature requests and questions that came up
during testing but were not reported as bugs.
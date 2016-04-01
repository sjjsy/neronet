Test Session Charter

# 1. What - tested areas

- General user experience
- Start guide
- Node specification: `nerocli --addnode`
- Experiment config files
- Experiment specification: `nerocli --addexp`
- Experiment submission: `nerocli --submit`
- Experiment result fetching: `nerocli --fetch`
- Overall status report: `nerocli --status`
- Experiment status report: `nerocli --status EXP_ID`

# 2. Why - goal and focus

The first purpose of our testing is to receive feedback from testers that are
completely unfamiliar with the Neronet system and its goals but might have
lots of ideas about how to improve its front end.

Another goal is to see how quickly they can make sense of the current start
guide without needing any other guidance. We want to use the peer team
testing to find out how the start guide and the software could be made clearer
and more understandable.

A third potential benefit of the testing is to discover potential errors in
important functions such as cluster specification, experiment specification
and experiment submission.

In addition to testing Neronet using the CLI, we will also test the GUI to
confirm that it can also be used to perform the most important functions
intuitively and without confusion.

# 3. How - approach

For the testing session we will meet at Maarintalo, in the class 240/241. To
test Neronet, we will use a UNIX system which can be a personal laptop or
simply a public access desktop at Maari. If need be we will set up a
`virtualenv` so that the installation doesn't conflict with other Python
packages on the computer. After this we instruct the testers to try and use
Neronet as a normal user might.

Testing data to be used is simply the example experiments we have prepared.

# 4. Exploration log

To be filled!

- SESSION START TIME: 13:10
- DURATION (hours): 4h
- TESTER: Kaarlo, Olli, and Joni
- BUILD: 0.3.1
- ENVIRONMENT: Teemu's, Tuomo's and Samuel's Linux laptops

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

- iss011 Color coding bug
- iss012 Think about what is interesting enough to take space in the GUI
- iss013 Fetch should happen automatically when changes are made
- iss014 Submit and other core buttons/stuff should be highlighted

## 4.4 Issues

Any observations, issues, new feature requests and questions that came up
during testing but were not reported as bugs.

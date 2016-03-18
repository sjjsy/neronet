Neronet quick start guide
=========================

What is Neronet
---------------

Neronet is a python-based, framework agnostic tool for computational
researchers that is made to enable easy

-  batch submission of experiment jobs to computing clusters
-  management of experiment queues
-  monitoring of logs and parameter values for ongoing experiments
-  access to experiment information during and after the run
-  configurable notifications on experiment state and progress
-  configurable criteria for experiment autotermination
-  logging of experiment history

Neronet can be used either via command-line interface or via GUI.
Neronet can be used on Linux and Unix machines, unfortunately Neronet
doesn’t currently support Windows.

This is a quick start quide; we will cover the most important commands
needed to use Neronet.

Neronet CLI
-----------

Step 1: Installation and configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1.1: Pip installation
^^^^^^^^^^^^^^^^^^^^^

Start by typing the following command on your local Linux or Unix
computer’s terminal:

::

    sudo pip install neronet

The neronet is then downloaded and installed to your local machine.

1.2 Setting up SSH login without password
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To avoid inputting your password every time Neronet uses a SSH connection
for something, it is advisable to set up passwordless SSH login for your clusters.

`Here 
<http://www.linuxproblem.org/art_9.html>`_ is a simple guide on how to do it.


1.3 Configuring your settings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Configure your clusters with the following command

::

    nerocli --addnode cluster_id ssh_address

For example, to configure kosh.aalto.fi as a usable node:

::
    
    blomqvt1@sromu:~$ nerocli --addnode kosh kosh.aalto.fi
    > ssh kosh.aalto.fi "cd ~/.neronet; PATH="~/.neronet/neronet:/usr/local/bin:/usr/bin:/bin" PYTHONPATH="~/.neronet" python -V"
    Cluster successfully accessed! Adding it...Defined a new cluster with ID "kosh"

Step 2: Specifying and submitting experiments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

2.1 Creating Neronet-compatible experiments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As an example, I have a folder ``experiments/theanotest`` under my home directory.
Inside this folder is a Python script that takes 3 commandline parameters:
N, feats, training_steps in that order, and would be run with, for example:

::

    python theanotest.py 400 784 10000

To make Neronet able to recognize this as an experiment, I 
create a **config.yaml** by using ``nerocli --template`` as such:

::

    nerocli --template theanotest python theanotest.py N feats training_steps

Which results in the following **config.yaml** being created in the current working directory

::

    theanotest:
        run_command_prefix: python
        main_code_file: theanotest.py
        parameters:
            N: 
            feats:
            training_steps:
        parameters_format: '{N} {feats} {training_steps} '

Then I edit the file to give values to the parameters

::

    theanotest:
        run_command_prefix: python
        main_code_file: theanotest.py
        parameters:
            N: 400
            feats: 784
            training_steps: 10000
        parameters_format: '{N} {feats} {training_steps} '

Finally, I move the file to ``experiments/theanotest/``.

2.3 Specifying the experiments so that Neronet knows of their existence
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To make Neronet recognize my experiment, I use ``nerocli --addexp <relativepath>``:

::

    blomqvt1@sromu:~$ nerocli --addexp experiments/theanotest
    Experiment(s) successfully defined.

2.4 Reviewing status information
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To see a basic status report of which clusters and experiments Neronet
knows of and what are the experiments’ state, I use ``nerocli --status``:

::
    
    blomqvt1@sromu:~$ nerocli --status
    ================Neroman=================

    ================User====================
    Name: 
    Email: 

    ================Clusters================
    kosh (kosh.aalto.fi, unmanaged)

    ================Experiments=============
    Defined:
    - theanotest

To view more specific information on an experiment I use ``nerocli --status <exp_id>``:

::

    blomqvt1@sromu:~$ nerocli --status theanotest

    theanotest
      Run command: python
      Main code file: theanotest.py
      Parameters: 400 784 10000
      Parameters format: {N} {feats} {training_steps}
      State: defined
      Last modified: 2016-02-26 14:02:03.935378



2.5 Submitting experiments to computing clusters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After you have successfully configured your experiments you can submit them to computing clusters with
``nerocli --submit <experiment_id> <cluster_id>`` as such:

::

    blomqvt1@sromu:~$ nerocli --submit theanotest kosh
    
    > rsync -az "/home/blomqvt1/projects/neronet/neronet" "/tmp/.neronet-theanotest"
    > cp -p "/home/blomqvt1/experiments/theanotest/theanotest.py" "/tmp/.neronet-theanotest/experiments/theanotest"
    > rsync -az -e "ssh" "/tmp/.neronet-theanotest/" "kosh.aalto.fi:~/.neronet"
    > ssh kosh.aalto.fi "cd ~/.neronet; PATH="~/.neronet/neronet:/usr/local/bin:/usr/bin:/bin" PYTHONPATH="~/.neronet" neromum --start"
    Neromum daemon started...
    Experiment theanotest successfully submitted to kosh

2.6 Fetching data of submitted experiments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To fetch data of submitted experiments, ``nerocli --fetch`` is used

::

    blomqvt1@sromu:~$ nerocli --fetch
    
    Fetching changes from cluster "kosh"...
    > rsync -az -e "ssh" "kosh.aalto.fi:~/.neronet/experiments/" "/home/blomqvt1/.neronet/results"
    > ssh kosh.aalto.fi "cd ~/.neronet; PATH="~/.neronet/neronet:/usr/local/bin:/usr/bin:/bin" PYTHONPATH="~/.neronet" neromum --input"
    Reading stdin...
    Read 39 bytes ("�}q(UactionqUclean_experimentsqU
    ").
    Read 17 bytes ("exceptionsq]qU
    ").
    Read 15 bytes ("theanotestqau.").
    Reading finished!
    Received {'action': 'clean_experiments', 'exceptions': ['theanotest']}
    Query "input" with ({'action': 'clean_experiments', 'exceptions': ['theanotest']},), {} to (127.0.0.1, 46826)...
    Received reply: {'data': {}, 'rv': 0, 'msgbody': '0 experiments cleaned.\n', 'uptime': 52.05758714675903}
    Reply {'data': {}, 'rv': 0, 'msgbody': '0 experiments cleaned.\n', 'uptime': 52.05758714675903}
    
    Updating experiment "theanotest"...

2.7: Other important Neronet CLI commands
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    nerocli --delexp experiment_id

Deletes a specified experiment from Neronet’s database.

::

    nerocli --clean

Wipes all Neronet related files e.g. Neronet’s database, user
configurations

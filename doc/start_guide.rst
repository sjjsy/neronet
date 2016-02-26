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

1.2: Configuring your settings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Configure your clusters with the following command

::

    nerocli --cluster cluster_id type ssh_address

where type can be unmanaged or slurm.

For example, to configure kosh.aalto.fi as an unmanaged cluster,
you can type

::
    
    nerocli --cluster kosh unmanaged kosh.aalto.fi

Configure your user details with the command

::

    nerocli --user name email

where the user name should be enclosed in quotation marks if it contains
spaces

Step 2: Specifying and submitting experiments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

2.1 Creating Neronet-compatible experiments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

-  Your experiments must be runnable in Terminal with a command of the
   format: ``run_command_prefix main_code_file parameter_string`` where
   **run\_command\_prefix**, **main\_code\_file** and **parameter\_string** are
   specified on the next step in config.yaml file.

2.2 Adding config.yaml to your experiment folder
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To configure your experiments to work with Neronet it is necessary to
add a configuration file named config.yaml to your experiment folder.
The format is as follows:

-  The config file follows standard yaml format conventions
-  Each config file should contain at least one experiment
-  Each experiment should have a unique name and the following
   variables:

-  run\_command\_prefix: the program used for running your experiment
   code file
-  main\_code\_file: name of the main code file
-  parameters: name value pairs of parameter values
-  parameters\_format: Specifies the parameter string parameter names
   written within parenthesis are replaced with the corresponding
   parameter values.

Example

config.yaml:

::

    test_experiment:
        run_command_prefix: python
        main_code_file: test_exp.py
        parameters:
                    n: 12
                    x: 17
        parameters_format: '-- {n} {x}'

From this config file Neronet would create an experiment named test_experiment that would be run with the
command

::

    python test_exp.py -- 12 17

Neronet will notify if the config file is not correctly formated

2.3 Specifying the experiments so that Neronet knows of their existence
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To complete specifying your experiments, type the following command

::

    nerocli --experiment ./relative/path/to/my/experimentfolder

Neronet will notify if the specifying of experiments fails for some
reason or another.

2.4 Reviewing status information
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To see a basic status report of which clusters and experiments Neronet
knows of and what are the experiments’ state, type

::

    nerocli --status

To view more specific information on an experiment you can use

::

    nerocli --status experiment_id

2.5 Submitting experiments to computing clusters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After you have successfully configured your experiments you can submit them to computing clusters with the
following command:

::

    nerocli --submit experiment_id cluster_id

Where cluster\_id is one of the previously defined clusters and
experiment\_id is one of the experiments specified.

2.6 Fetching data of submitted experiments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To fetch data of submitted experiments, type

::

    nerocli --fetch

This will attempt to fetch data on all submitted experiments.

2.7: Other important Neronet CLI commands
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    nerocli --delete experiment_id

Deletes a specified experiment from Neronet’s database.

::

    nerocli --clean

Wipes all Neronet related files e.g. Neronet’s database, user
configurations

Step 3: A simple use case
~~~~~~~~~~~~~~~~~~~~~~~~~

As an example, I have a folder ``experiments/theanotest`` under my home directory.
Inside this folder is a Python script that takes 3 commandline parameters:
N, feats, training_steps in that order, and would be run with, for example:

::

    python theanotest.py 400 784 10000

To make Neronet able to recognize this as an experiment, I create a ``config.yaml``
in the folder as such: 

::

    theanotest:
        run_command_prefix: python
        main_code_file: theanotest.py
        outputs: 'results'
        parameters_format: '{N} {feats} {training_steps}'
        parameters:
            N: 400 
            feats: 784
            training_steps: 10000

Then I make Neronet recognize it with ``nerocli --experiment relativepath``:

::
    
    blomqvt1@sromu:~$ nerocli --experiment experiments/theanotest

Then with ``nerocli --status`` I can check what Neronet knows.

::

    blomqvt1@sromu:~$ nerocli --status

    ================Neroman=================

    ================User====================
    Name: 
    Email: 

    ================Clusters================
    Clusters:
    No clusters defined

    ================Experiments=============
    Defined:
    - theanotest

And with ``nerocli --status experiment_id`` you can get more specific
information about the experiment:

::

    blomqvt1@sromu:~$ nerocli --status theanotest

    theanotest
      Run command: python
      Main code file: theanotest.py
      Parameters: 400 784 10000
      Parameters format: {N} {feats} {training_steps}
      State: defined
      Last modified: 2016-02-26 14:02:03.935378

Then, define a cluster:

::

    blomqvt1@sromu:~$ nerocli --cluster kosh unmanaged kosh.aalto.fi

    > ssh kosh.aalto.fi "cd ~/.neronet; PATH="~/.neronet/neronet:/usr/local/bin:/usr/bin:/bin" PYTHONPATH="~/.neronet" python -V"
    The cluster seems to be online!
    Defined a new cluster named kosh

Now that everything is set up, we can submit the experiment.

::

    blomqvt1@sromu:~$ nerocli --submit theanotest kosh
    
    > rsync -az "/home/blomqvt1/projects/neronet/neronet" "/tmp/.neronet-theanotest"
    > cp -p "/home/blomqvt1/experiments/theanotest/theanotest.py" "/tmp/.neronet-theanotest/experiments/theanotest"
    > rsync -az -e "ssh" "/tmp/.neronet-theanotest/" "kosh.aalto.fi:~/.neronet"
    > ssh kosh.aalto.fi "cd ~/.neronet; PATH="~/.neronet/neronet:/usr/local/bin:/usr/bin:/bin" PYTHONPATH="~/.neronet" neromum --start"
    Neromum daemon started...
    Experiment theanotest successfully submitted to kosh

Then you can update the status of all experiments with ``nerocli --fetch``:

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

Changes to the experiment statuses can be followed by using ``nerocli --status`` as demonstrated before.

::

    blomqvt1@sromu:~$ nerocli --status
    ================Neroman=================
    
    ================User====================
    Name: 
    Email: 
    
    ================Clusters================
    Clusters:
    - kosh (unmanaged, kosh.aalto.fi)
    
    ================Experiments=============
    Finished:
    - theanotest

Intermediate results can be found in the folder ``~/.neronet/results/experiment_id``.

When the experiment is finished the final results are then moved under the original experiment folder, in this example
to ``~/experiments/theanotest/results/theanotest/``.

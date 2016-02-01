Neronet quick start guide
=========================

What is Neronet
---------------

Neronet is a python-based, framework agnostic tool for computational
researchers that is made to enable easy

-  batch submission of experiment jobs to computing clusters
-  management of experiment queues
-  monitoring of ongoing experiments’ logs and parameter values
-  access to experiment information during and after the run
-  configurable notifications on experiment state and progress
-  configurable criteria for experiment autotermination
-  logging of experiment history

Neronet can be used either via command-line interface or via GUI.
Neronet can be used on Linux and Unix machines, unfortunately Neronet
doesn’t currently support Windows.

This is a quick start quide; we will cover the most important

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

    nerocli --cluster cluster_id ssh_address type

where type can be unmanaged or slurm

Configure your user details with the command

::

    nerocli --user name email

where the user name should be enclosed in quotation marks if it contains
spaces

Step 2: Specifying and submitting experiments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

2.1 Creating Neronet-compatible experiments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

-  Your experiments must be runnable on Terminal with a command of the
   format: ‘run\_command\_prefix main\_code\_file [parameters]’ where
   run\_command\_prefix, main\_code\_file and parameter\_string are
   specified on the next step in config.yaml file.

2.2 Adding config.yaml to your experiment folder
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To configure your experiments to work with Neronet it is necessary to
add a configuration file named config.yaml to your experiment folder.
The format is as follows:

-  The config file follows standard yaml format conventions
-  Each config file should contain at least one experiment
-  Each experiment should have an unique name and the following
   variables:

   -  run\_command\_prefix: the program used for running your experiment
      code file
   -  main\_code\_file: name of the main code file
   -  parameters: name value pairs of parameter values
   -  parameters\_format: a string specifying the order of the parameter
      values

Example

config.yaml:

::

    test_experiment:
        run_command_prefix: python
        main_code_file: test_exp.py
        parameters:
            n: 12
            x: 17
        parameters_format: '{n} {x}'

This config file would create an experiment that would be run with the
command

::

    python test_exp.py 12 17

Neronet will notify if the config file is not correctly formated

2.3 Specifying the experiments so that Neronet knows of their existence
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To complete specifying your experiments, type the following command

::

    nerocli --experiment folder

Where folder is the absolute

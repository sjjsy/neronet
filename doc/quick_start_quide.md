#Neronet quick start guide

##What is Neronet

Neronet is a python-based, framework agnostic tool for computational researchers
 that is made to enable easy

- batch submission of experiment jobs to computing clusters
- management of experiment queues
- monitoring of ongoing experiments' logs and parameter values
- access to experiment information during and after the run
- configurable notifications on experiment state and progress
- configurable criteria for experiment autotermination
- logging of experiment history

Neronet can be used either via command-line interface or via GUI. Neronet can be 
used on Linux and Unix machines, unfortunately Neronet doesn't currently support 
Windows.

This is a quick start quide; we will cover the most important 

##Neronet CLI

###Step 1: Installation

####1.1: Pip installation

Start by typing the following command on your local Linux or Unix computer's 
terminal:

```
sudo pip install neronet
```

The neronet is then downloaded and installed to your local machine.

####1.2: Configuring your settings

Find the folder '~/.neronet' that was created during pip installation, open it
and type in your preferences and initial cluster setup to preferences.yaml and 
clusters.yaml. The formats are as follows:

clusters.yaml:
```
clusters:
  triton:
    ssh_address: triton.aalto.fi
    type: unmanaged
  gpu1:
	ssh_address: gpu1
	type: unmanaged
  gpu2:
	ssh_address: gpu1
	type: unmanaged
groups:
  gpu: [gpu1, gpu2]
```

preferences.yaml:
```
name: John Doe
email: john.doe@gmail.com
default_cluster: triton
```

If the format of the files seems unclear, see the User Manual for further 
instructions.

Proceed by typing the following command to see if the installation and 
configuration succeeded:

```
nerocli --status
```

The program will notify you if the installation or configuration failed for some
 reason or another.

###Step 2: Specifying and submitting experiments

####2.1 Creating Neronet-compatible experiments

- Write your codefiles and/or parameterfiles to a single folder
- Your experiments must be runnable on Terminal with a command of the format:
  'RUN_COMMAND_PREFIX MAIN_CODE_FILE PARAMETER_STRING' where RUN_COMMAND_PREFIX, 
  MAIN_CODE_FILE and PARAMETER_STRING are specified on the next step in config.yaml
  file.

####2.2 Adding config.yaml to your experiment folder

To configure your experiments to work with Neronet it is necessary to add 
a configuration file named config.yaml to your experiment folder. The format is
as follows:

config.yaml:
```
collection: None
run_command_prefix: 'python3'
main_code_file: 'main.py'
logoutput: 'results'
parameters:
    count: 6
    interval: 2.0
parameters_format: '{count} {interval}'
sleep1:
    parameters:
        count: [4, 5, 6, 7]
        interval: 3
    sleep2:
        parameters:
            interval: [100,200]
        parameters_format: '{interval} {count}'
sleep3:
    sleep5:
        logoutput: 'output'
sleep4:
    run_command_prefix: 'python'
    sleep6:
        parameters:
            count: 3
        sleep7:
            parameters:
                count: 7
                interval: 1
```

A few notes regarding the format:
- The information on the config.yaml file is divided to blocks that have the 
  same indentation.
- The collection-attribute must either be None or any unique value 
- Each experiment specification must begin with a row containing the 
  experiment id (f.ex in the example above six experiments are specified: 
  sleep1, sleep2, sleep3, sleep4, sleep5, sleep6) and be followed by a block 
  containing all the experiment's attributes. The experiment ids must 
  be unique.
- Each different experiment specification must have the following attributes
    - main_code_file: The path to the code file that is to be run when executing 
	  the experiment
	- run_command_prefix: The prefix of the run command f.ex 'python3'
	- parameters: This attribute is followed by a block containing all the 
	  unique parameters of this specific experiment. Parameter names can be 
	  arbitrary.
	- parameters_format: Specifies the order in which the parameters are given to 
	  the experiment code file in the form of a string. Write the attribute 
	  value within single quotes. Parameter names written within braces will be 
	  replaced by their values defined in the *parameters* section. F.ex in the 
	  example above sleep2 --parameters_format defines a parameter string 
	  'kh nyt data/2.txt 400'. You can escape braces and special characters 
	  with backslashes in case your parameter names contain braces.
- If multiple experiments have the same attribute values, it is not necessary 
  to re-write every attribute for every experiment. The experiments defined in 
  inner blocks automatically inherit all the attribute values specified in 
  outer blocks. For example in the example above all the experiments inherit 
  the main_code_file and logoutput values from the outmost block and sleep2 the 
  parameter 'count' values from sleep1. If you don't want to inherit a specific 
  value, just specify it again in the inner block and it is automatically 
  overwritten. For example in the example above sleep2 uses different parameter 
  'interval' than its parent sleep1.
- If you place multiple parameter values within brackets and separated by a 
  comma (like in the example above sleep1 -- count: [4,5,6,7] ) Neronet will 
  automatically create different version of the experiment for each value 
  specified within brackets.
- It is also possible to configure Neronet to send automatic warnings or 
  autoterminate an experiment. For that, please see further instructions in user
  manual.

####2.3 Specifying the experiments so that Neronet knows of their existence

To complete specifying your experiments, type the following command on your local
mchine's terminal or command line.

```
nerocli --experiment FOLDER
```
Where FOLDER is the absolute path to your experiment folder. Neronet will notify
if the specifying of experiments fails for some reason or another.

####2.4 Submitting experiments to computing clusters

After you have successfully configured your experiments (You can make sure of
that by typing 'nerocli --status' after which you will see a list of all the
specified experiments and clusters, and your personal information) you can submit
them to computing clusters with the following command:

```
nerocli --submit CLUSTER_ID EXPERIMENT_ID
```
Where CLUSTER_ID is one of the previously defined clusters or cluster groups 
and EXPERIMENT_ID is one of the experiment ids defined in config.yaml.

###Step 3: Other important Neronet CLI commands

Delete a specified experiment from Neronet's database:
```
Uage: nerocli --delete EXPERIMENT_ID
Example: nerocli --delete sleep1
```

Adds a cluster via command line
```
Usage: nerocli --cluster ID SSH_ADDRESS TYPE
Example: nerocli --cluster triton triton.cs.hut.fi slurm
```

Get a single experiment's status report:
```
Usage: nerocli --status EXPERIMENT_ID
Example: nerocli --status sleep1
```



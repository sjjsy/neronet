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
  cluster1:
    ssh_address: cluster1.example.fi
    type: unmanaged
  cluster2:
	ssh_address: cluster2.example.fi
	type: unmanaged
groups:
  gpu: [cluster1, cluster2]
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
```

See user manual for further instructions.

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

Fetch data of submitted experiments:
```
nerocli --fetch
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

###nerogui
Using nerogui is as simple as nerocli.

Nerogui requires pyqt4. You an download it by following
```
apt-get install python-qt4
```

Start nerogui program by writing
```
nerogui
```

You can view your defined experiments in the leftmost view.
You can ciew your specified clusters in view next to experiment view.

You can add new experiments by pressing "add experiments" and then selecting the folder with "config.yaml"

You can add new clusters by typing server info to text fields and pressing "add cluster"
You can update your clusters by clicking cluster name. Information of corresponding cluster is added to cluster fields.

You can submit your experiments by selecting experiment and cluster from list, and then presing submit.



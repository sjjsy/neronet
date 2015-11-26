==================
Neronet User Guide
==================

Command Line Interface
----------------------

**Installation**

Before installing neronet check that you have Python 3.5 installed on your local machine and the clusters.

Download neronet folder
and open clusters.yaml in your favorite text editor.
Specify your initial cluster setup using the following format:

The specification of a cluster must start with the user-specified cluster-id 
on a separate line. The following lines containing the cluster's information
must be indented and contain at least the following attributes:
ssh_address: (f.ex  triton.aalto.fi) and type: (either 'unmanaged' or 'slurm').

Additionally, it is possible to specify the maximum queue with the attribute
queue_max and save important information on the cluster such as the cluster's 
hard disk space with the hard_disk_space attribute and the cluster's
CPU with the cpu attribute. You can also write all of the cluster's hardware information
under the hardware attribute.

It is also possible to group some of your unmanaged nodes under a single cluster name
using the following format: GROUP_ID: [NODE_ID, NODE_ID, ...]

Neronet supports slurm clusters and unmanaged nodes.

*Example:*
::
	triton:
	  ssh_address: triton.aalto.fi
	  type: slurm  
	  default_log_path:
	  queue_max: 20
	  hard_disk_space: 1000GB
	  cpu: 
	gpu1:
	  ssh_address: gpu1
	  type: unmanaged
	  hardware: 
	gpu2:
	  ssh_address: gpu1
	  type: unmanaged
	gpu: [gpu1, gpu2]


*After that open preferences.yaml and fill in your preferences using the following format:*
::
	name: John Doe
	email: john.doe@gmail.com


Then start neronet. The program will notify you if the installation failed. 

**Start neronet**

Neronet CLI starts by running neroman.py on the command line.

*Example:*
::
	python3.5 neroman.py


**Specify clusters**

You can specify clusters either via command line or by manually updating
the clusters.yaml file. See the section *Installation* to get information
on the format to use when manually updating the clusters.yaml file.

*To add clusters via command line use the following format:*
::
	Usage: neroman --cluster ID SSH_ADDRESS TYPE
	Example: neroman --cluster triton triton.cs.hut.fi slurm


ID is a user defined id of the cluster
SSH_ADDRESS is the ssh address of the cluster
TYPE is either slurm or unmanaged

The information given via CLI is then automatically updated to clusters.yaml.
If you want to save other information on a specific cluster besides the cluster's
address, name and type, you must manually write them to the clusters.yaml file.

**Specify experiments**

Start by writing your experiment code and saving all experiments you deem somehow
related to a single folder. Then include a YAML configuration file in your folder
adn name it 'config.yaml'. In the configuration file you are to specify all the
different experiments you want to run using the following format:


- The information on the config.yaml file is divided to blocks that have the same indentation.
- ID-attribute must be specified on the topmost row. Must be unique.
- Each experiment specification must begin with a row containing the experiment id (format: experiment_Id: ID, f.ex experiment_Id: lang_exp1) and be followed by a block containing all the experiment's attributes. The experiment ids must be unique within the same config file.
- Each different experiment must have the following attributes
	- main_code_file: The path to the code file that is to be run when executing the experiment
	- run_command_prefix: The prefix of the run command f.ex 'python3'
	- logoutput: The location to which the log output of the experiment is to be written. Can be either stdout or a file path.
	- parameters: This attribute is followed by a block containing all the unique parameters of this specific experiment. Parameter names can be arbitrary.
	- parameter_format: The format in which the parameter values are given to the experiment code file.
- Additionally, if you want neronet to autoterminate an experiment or give you a warning under certain circumstances you can use the warning-attribute. Neronet supports warnings and autotermination based on a variable exceeding, falling below or reaching a predetermined value. The warning-attribute must be followed by a block containing the following attributes
 	- The warning condition is specified by the following three attributes
	 	- variablename: This is the name of the variable you want to monitor
	 	- killvalue: This is the value to which you want neronet to compare the monitored variable
	 	- comparator: Either >, < or = Use > if you want a warning when the value of the variable monitored exceeds killvalue, < if you want a warning when the variable falls below killvalue and = if you want a warning when the variable reaches killvalue.
 	- when: The value of this attribute can be either 'immediately' or 'time MINUTES' where MINUTES is the time interval in minutes after which the warning condition is checked.
 	- action: Specifies what you want neronet to do when the warning condition is fulfilled. The value of this attribute is either 'kill' (if you want the experiment to be terminated when the warning condition is fulfilled), 'warn' (if you only want to see a warning message the next time you check the experiment status) or email (if you want to receive a warning email when the warning condition is fulfilled)
 	- The log output from the experiment code must contain rows of the format: 'VARIABLENAME VALUE'. So that neronet is able to follow the variable values. For example in the example below the log output of lang_exp1 must contain rows like 'error_rate 24.3334', 'error_rate 49', 'error_rate 67.01', etc...
- If multiple experiments have the same attribute values, it is not necessary to re-write every attribute for every experiment. The experiments defined in inner blocks automatically inherit all the attribute values specified in the outer blocks. For example in the example below 'lang_exp1' and 'lang_exp2' inherit the run_command_prefix, main_code_file and logoutput values from the outmost block and lang_exp3 inherits all the parameter values from lang_exp1. If you don't want to inherit a specific value, just specify it again in the inner block and it is automatically overwritten. For example in the example below lang_exp3 uses different huperparamz and parameter_format values than its parent lang_exp1.
- Brackets

*Example:*
::
	ID: lang_exp
	run_command_prefix: python3
	main_code_file: main.py
	logoutput: stdout
	experiment_Id: lang_exp1
		parameters:
			hyperparamx: [1,2,34,20]
			hyperparamy: 2
			data_file: data/1.txt
			hyperparamz: 2
		parameter_format: '--hyperparamx %s{hyperparamx} %hyperparamy
		warning:
			variablename: error_rate
			killvalue: 50
			comparator: >
			when: time 6000
			action: kill

		experiment_Id: lang_exp3 #This inherits all the parameters from lang_exp1
			parameters:
				hyperparamz: 2 #This parameter is overwritten
			parameter_format: --hyperparamx %s{hyperparamx} %hyperparamy

	experiment_Id: lang_exp2
		run_command_prefix: python2
		main_code_file: main2.py
		parameters:
		    hyperparamx: kh
		    hyperparamy: nyt
		    data_file: data/2.txt
		    hyperparamz: 400
		parameter_format: '--hyperparamx %s{hyperparamx} %hyperparamy


After your experiment folder contains the config file of the correct format and all the code and parameter files, you can submit it to neronet queue using the following command::
	Usage: neroman --experiment FOLDER
	Example: neroman --experiment ~/experiments/lang_exp


**Delete Experiments**

*The following command deletes a specified experiment from the experiment queue:*
::
	neroman --delexp EXPERIMENT_ID
	neroman --delexp FOLDER


**Submit experiments and batches of experiments**

*To get info on clusters before submitting experiments type the following command:*
::
	Usage: neroman --submit CLUSTER_ID EXPERIMENT_ID
	Example: neroman --submit triton lang_exp3


EXPERIMENT_ID is the 'ID' attribute defined on the topmost row of the experiment folder's config.yaml. Alternatively, if you only want to submit a certain experiment within a folder, you can use the format 'ID/experiment_Id' (see *specifying experiments* to find out what these attributes are)
Using 'all' as EXPERIMENT_ID will submit all specified but not submitted experiments.

CLUSTER_ID can be any cluster id or cluster group id specified in the clusters.yaml file or via CLI.
Using 'any' as CLUSTER_ID will divide the work (if it can be divided) and submit it to all free clusters.

*Tasks can be submitted also by logical arguments:*
::
	Usage: neroman --submit CLUSTER_ID ARGUMENT

	#Specify an experiment and submit it instantly
	Example: neroman --submit triton ~/experiments/lang_exp x

	#Submit all experiments that were modified since 2015-11-23
	Example: neroman --submit triton tmod>2015-11-23

	#Submit all that have a specified parameter
	Example: neroman --submit triton params=*data/1.txt*

	#Submit all experiments from the queue
	Example: neroman --submit any all


**Monitoring log output**

*Example:*
::
	Usage: neroman --monitor EXPERIMENT_ID
	Example: neroman --monitor lang-exp/lang_exp3


*The output will be of the following format:*
::
	Cluster
	Starting time
	Log output

**Status report**

The status command gives status information regarding configurations and any
specified clusters and experiments.

*Example:*
::
	Usage: neroman --status [ARGS]


ARGS can refer to experiment or cluster IDs, or be collection specifiers.
::
	Example: neroman --status # Overall status information
	#Prints the list of experiments, their overall statuses
	#(in queue/running/finished/terminated) and locations (queue/CLUSTER_ID)

	Example: neroman --status lang_exp/lang_exp3 # experiment status
	#Prints the experiment's parameters, times when the experiment was specified,
	#whether the experiment is in the queue, running, finished and/or terminated
	#and where the experiment is running if it is running
	#If the experiment is finished this also prints the experiment's final output.

	Example: neroman --status 'tsub>yesterday' # collection status
	#Prints the list of experiments specified since yesterday and their overall
	statuses (in the queue/running/finished/terminated)) and locations (queue/CLUSTER_ID)

	Example: neroman --status queue # all the experiments in the queue
	#Prints a list of experiments not submitted to any cluster and the
	#times when they were specified.

	Example: neroman --status triton # cluster status
	#Prints the list of experiments running in the given cluster and their starting times

	Example: neroman --status clusters # all cluster's statuses


**GUI**

**Installation**

**Specify clusters**

**Specify experiments**

**Submit experiments unmanaged**

**Submit experiments slurm**

**Submit batches of experiments**

**Monitoring log output**

**Experiment status report**

**Collection status report**

**Neronet status report**

**Backup**


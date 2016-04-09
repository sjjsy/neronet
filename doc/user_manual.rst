==================
Neronet User Guide
==================

Contents
--------


- **Contents**
- **Introduction**
- **Installation**
- Command Line Interface:
	- Using Neronet CLI
	- Specifying Computing Nodes in Neronet CLI
	- Specifying Clusters and Cluster Groups by Manually Updating Clusters.yaml
	- Deleting Computing Nodes in Neronet CLI
	- Specifying and Configuring Experiments in Neronet CLI
	- Deleting Defined Experiments from Neronet
	- Submitting Experiments to Computing Clusters
	- Fetching data about submitted experiments
	- Terminating a Currently running experiment
	- Status report
	- Cleaning Neronet's databases
	- Example use case
- GUI:
	- Starting Neronet GUI
	- Specifying and Configuring Experiments in Neronet GUI
	- Deleting Defined Experiments from Neronet
	- Submitting Experiments and Batches of Experiments to Computing Clusters
	- Specifying Clusters in Neronet GUI
	- Monitoring Log Output in Neronet GUI
	- Status report in Neronet GUI


Introduction
------------

Neronet is a python-based, framework agnostic tool for computational researchers that is made to enable easy

- specification of computational experiments and inheritance of parameter values
- batch submission of experiment jobs to computing clusters
- monitoring of logs and parameter values for ongoing experiments
- access to experiment information during and after the run
- configurable notifications on experiment state and progress
- configurable criteria for experiment autotermination
- logging of experiment history

Neronet can be used either via command-line interface or via GUI.


Installation
------------

All components of the neronet application, including both the parts run in clusters and the parts run in the researcher's local machine are implemented using python 2.7, so before installation please make sure that the correct version of python is installed on your local machine and on the computing clusters you intend to be use. Using other python versions may cause complications and is therefore not recommended. Then download neronet folder and proceed by setting up your initial cluster setup and setting up your preferences.

**1. Pip Installation**

Start by running the command below on the command line of your local machine. Note: python 2.7 is required.

*Install neronet:*
::
	sudo pip install neronet

The command will load all components related to neronet and install them to the system. It will also create the folder '~/.neronet' that contain your preferences and cluster setup. Proceed by opening the folder and then defining your initial cluster setup and preferences in the respective files.

**2. Setting up personal Information and preferences:**

Open the file ~/.neronet/preferences.yaml and fill in your name, email and default cluster using the following format.

*Example:*
::
	name: John Doe
	email: john.doe@gmail.com
	default_cluster: triton


If you followed the instructions, your neronet application should be ready to run now. Proceed by starting neronet. The program will notify you if the installation failed for one reason or another.

======================
Command Line Interface
======================

Using Neronet CLI
--------------------

To start your Neronet CLI application, run nerocli on your local machine's command line.

*Example:*
::
	nerocli --status


Specifying Computing Nodes in Neronet CLI
----------------------------------

You can specify clusters either via command line or by manually updating the clusters.yaml file. See the next section for more information on the format when updating the clusters.yaml file manually.

*To add computing nodes via command line use the following format:*
::
	Usage: nerocli --addnode ID SSH_ADDRESS
	Example: nerocli --addnode triton triton.cs.hut.fi


ID is a user defined id of the cluster, SSH_ADDRESS is the ssh address of the cluster.

The information given via CLI is then automatically updated to clusters.yaml. If you want to save other information about a specific cluster besides the cluster's address and id, you must manually write them to the clusters.yaml file.


Specifying Clusters and Cluster Groups by Manually Updating Clusters.yaml
-------------------------------------------------------------------------

Although nodes can be easily specified via neronet CLI or GUI, manually updating the config files gives the user some additional options and is sometimes more versatile.

Open ~/.neronet/clusters.yaml using your favorite text editor and fill in the following information.

The format of clusters.yaml is as follows. From here on out we will explain the formats of important files by first showing an example file and then explaining the important points.

*Example:*
::
    clusters:
	    triton:
	      ssh_address: triton.aalto.fi
	      hard_disk_space: 1000GB
	    gpu1:
	      ssh_address: gpu1
	    gpu2:
	      ssh_address: gpu2
	groups:
	    gpu: [gpu1, gpu2]



The specification of a cluster must start with the user-specified cluster-id on a separate line. The following lines containing the cluster's information must be indented and contain at least the ssh_address: (f.ex  triton.aalto.fi).

Additionally, it is possible to specify optional information on the node such as the hard disk space. However, these are purely for the user and are not used internally.

It is also possible to group some of your nodes under a single virtual cluster name using the following format: GROUP_ID: [NODE_ID, NODE_ID, ...] (f.ex 'gpu: [gpu1, gpu2]' in the example above). Then later on you can submit your experiments to that virtual cluster name and let neronet automatically divide the work between the actual nodes.


Deleting Computing Nodes in Neronet CLI
---------------------------------------

If you want to remove all information regarding a specific computing node from neronet's database, type the following command:

*Remove a computing node:*
::
    Usage: nerocli --delnode ID
	Example: nerocli --delnode triton
	


Specifying and Configuring Experiments in Neronet CLI
-----------------------------------------------------

Neronet supports experiments written using any programming language or framework as long as the experiments are runnable with a command of the format 'RUN_COMMAND-PREFIX CODE_FILE PARAMETERS', f.ex. 'python2.7 main.py 1 2 3 4 file.txt'

Start by writing your experiment code and save all experiments you deem somehow related to a single folder. Then include a YAML configuration file in your folder and name it 'config.yaml'.It is also possible to create the YAML configuration file template with the following command:

*To create a config.yaml template use the following command:*
::
	Usage: nerocli --template EXP_ID RUN_COMMAND-PREFIX CODE_FILE PARAMETERS
	Example: nerocli --template theanotest python theanotest.py N feats training_steps


In the configuration file you are to specify all the different experiments you want to run using the following format. Please read this section carefully for it contains plenty of important information.

*config.yaml:*
::
	run_command_prefix: python3
	main_code_file: main.py
	logoutput: stdout
	+lang_exp1:
		parameters:
			hyperparamx: [1,2,34,20]
			hyperparamy: 2
			data_file: data/1.txt
			hyperparamz: 2
		parameter_format: '{hyperparamx} {hyperparamy} {data_file} {hyperparamz}'
		conditions:
			error_rate_over_50:
				variablename: error_rate
				killvalue: 50
				comparator: gt
				when: time 6000
				action: kill
			error_rate_over_35:
				variablename: error_rate
				killvalue: 35
				comparator: geq
				when: time 6000
				action: warn

		+lang_exp3:
			parameters:
				hyperparamz: 2

	+lang_exp2:
		run_command_prefix: python2
		main_code_file: main2.py
		parameters:
		    hyperparamx: kh
		    hyperparamy: nyt
		    data_file: data/2.txt
		    hyperparamz: 400
		parameter_format: '{hyperparamx} {hyperparamy} {data_file} {hyperparamz}'


- The information on the config.yaml file is divided to blocks that have the same indentation.
- Each experiment specification must begin with a row containing the experiment id (f.ex in the example above three experiments are specified: lang_exp1, lang_exp2 and lang_exp3) and be followed by a block containing the experiment's attributes. Do not use the reserved words, list of which can be found at the end of this section. The experiment ids must be unique.
- Experiment ids must begin with '+' character, otherwise neronet won't recognise the new experiment.
- Each different experiment specification must have the following attributes
	- main_code_file: The path to the code file that is to be run when executing the experiment
	- run_command_prefix: The prefix of the run command f.ex 'python2'
	- logoutput: The location to which the log output of the experiment is to be written. Can be either stdout or a file path.
	- parameters: This attribute is followed by a block containing all the unique parameters of this specific experiment. Parameter names can be arbitrary.
	- parameter_format: Specifies the order in which the parameters are given to the experiment code file in the form of a string. Write the attribute value within single quotes. Parameter names written within braces will be replaced by their values defined in the *parameters* section. F.ex in the example above lang_exp2 --parameter_format defines a parameter string 'kh nyt data/2.txt 400'. You can escape braces and special characters with backslashes in case your parameter names contain braces.
	- Your experiments should be runnable with a command of the form 'RUN_COMMAND_PREFIX MAIN_CODE_FILE PARAMETER_STRING' F.ex in the example above lang_exp2 must be runnable with the command 'python2 main2.py kh nyt data/2.txt 400'**

- Additionally, if you want neronet to autoterminate an experiment or give you a warning under certain circumstances you can use the conditions-attribute. Neronet supports warnings and autotermination based on a variable exceeding, falling below or reaching a predetermined value. The conditions-attribute must be followed by a block containing the specifications of the conditions and actions to perform
	- Start by giving a unique ID to your condition. f.ex in the example above 'lang_exp1' has two conditions set: 'error_rate_over_50' and 'error_rate_over_35'. Do not use the reserved words, list of which can be found at the end of this section. Then specify the following attributes on the following block.
	- variablename: This is the name of the variable you want to monitor
	- killvalue: This is the value to which you want neronet to compare the monitored variable
	- comparator: Either 'gt' (greater that), 'lt' (less than), 'eq' (equal to), 'geq' (greater than or equal to) or 'leq' (less than or equal to). Use 'gt' if you want a warning when the value of the variable monitored exceeds killvalue, 'lt' if you want a warning when the variable falls below killvalue and 'eq' if you want a warning when the variable reaches killvalue.
 	- when: The value of this attribute can be either 'immediately' or 'time MINUTES' where MINUTES is the time interval in minutes after which the warning condition is checked and action performed.
 	- action: Specifies what you want neronet to do when the warning condition is fulfilled. The value of this attribute is either 'kill' (if you want the experiment to be terminated when the warning condition is fulfilled) or 'warn' (if you want to see a warning message when the condition is fullfilled)
 	- The log output from the experiment code must contain rows of the format: 'VARIABLENAME VALUE'. So that neronet is able to follow the variable values. F.ex. in the example above the log output of lang_exp1 must contain rows of the form 'error_rate 24.3334', 'error_rate 49', 'error_rate 67.01', etc... The row must not contain anything else.
- If multiple experiments have the same attribute values, it is not necessary to re-write every attribute for every experiment. The experiments defined in inner blocks automatically inherit all the attribute values specified in outer blocks. For example in the example above 'lang_exp1' and 'lang_exp2' inherit the run_command_prefix, main_code_file and logoutput values from the outmost block and lang_exp3 inherits all the parameter values from lang_exp1. If you don't want to inherit a specific value, just specify it again in the inner block and it is automatically overwritten. For example in the example above lang_exp3 uses different hyperparamz and parameter_format values than its parent lang_exp1.
- If you place multiple parameter values within brackets and separated by a comma (like in the example above lang_exp1 -- hyperparamx: [1,2,34,20])Neronet will automatically generate different experiments for each value specified within brackets. (f.ex lang_exp1 would be run with the parameters '1 2 data/1.txt 2', '2 2 data/1.txt 2', '34 2 data/1.txt 2' and '20 2 data/1.txt 2')

After your experiment folder contains the config file of the correct format and all the code and parameter files, you can then submit the folder to your Neronet application with the following command.

*Submit the experiment folder to neronet locally:*
::
	Usage: nerocli --addexp FOLDER
	Example: nerocli --addexp ~/experiments/lang_exp

**Reserved Words:**
::
	ID
	run_command_prefix
	main_code_file
	logoutput
	parameters
	parameter_format
	warning:
	variablename
	killvalue
	comparator
	when
	action



Deleting Defined Experiments from Neronet
-----------------------------------------

To delete a specified experiment from your Neronet application's database you can use the following command.

*Example:*
::
	nerocli --delexp EXPERIMENT_ID

Using the command above doesn't delete the experiment folder or any files within it. It only removes the experiment's information from Neronet's database and if the experiment is running, terminates it. It also doesn't affect the experiment's child experiments.


Submitting Experiments to Computing Clusters
--------------------------------------------

The following command will submit an experiment to a specified computing node or cluster.

*Submit an experiment to a computing node or cluster:*
::
	Usage: nerocli --submit EXPERIMENT_ID CLUSTER_ID 
	Example: nerocli --submit lang_exp triton 


EXPERIMENT_ID is the name of the experiment you are about to submit.

CLUSTER_ID can be any cluster id or cluster group id specified in the clusters.yaml file or via CLI or GUI.
If you have specified a default cluster in preferences.yaml (see *Installation*), you can leave CLUSTER_ID blank to automatically submit your experiments to the specified default cluster. F.ex 'submit lang_exp'.


Fetching data about submitted experiments
-----------------------------------------

To see the current state of the submitted experiments it is necessary to first fetch the data from clusters. In Neronet CLI this is done by typing the following command:

::
    nerocli --fetch

After that you can see the current state of your experiments by typing:

::
    nerocli --status


Terminating a Currently running experiment
------------------------------------------

If you need to manually terminate an experiment thst is currently running in a cluster, type the following command

*Terminate an experiment:*
::
    nerocli --terminate EXPERIMENT_ID
    
 

Status report
-------------

The status command gives status information regarding configurations and any
specified clusters and experiments.

*Example:*
::
	Usage: nerocli --status [ARGS]


ARGS can refer to experiment or cluster IDs.

*Overall status:*
::
	nerocli --status

The command above will print the overall status information. That is, printing the number of experiments with each of the different experiment states, the list of defined clusters and their current states and finally the list of experiments and their current states.

*Experiment status:*
::
	nerocli --status lang_exp3

*Cluster status:*
::
	Usage: nerocli --status CLUSTER_ID
	Example nerocli --status triton
	
Cleaning Neronet's databases
----------------------------

If you want to remove all data currently existing in neronet's databases, that is all specified experiments, their results and information on computing nodes and clusters, type the following command:

*Clean neronet's databases*
::
    nerocli --clean


Example use case
----------------
Assume we have folder ``~/mytheanotest`` which contains an experiment named
``script.py`` and we want to submit it to ``kosh.aalto.fi`` to be run
there. We proceed as follows:

Define a cluster where the experiment is to be run:
``nerocli --addnode kosh kosh.aalto.fi``

Neronet requires some information about each experiment, which is why we
create the file ``~/mytheanotest/config.yaml`` with the following content::

		```
		collection: None
		run_command_prefix: 'python'
		main_code_file: 'script.py'
		outputs: 'results'
		parameters_format: '{N} {feats} {training_steps}'
		theanotest:
		    parameters:
		        N: 400
		        feats: 784
		        training_steps: 10000
		```

Now we let Neronet know about the experiment by registering it:
``nerocli --addexp ~/mytheanotest``

Finally, we submit the experiment to be run in the cluster:
``nerocli --submit theanotest kosh``

Before submitting of course you need to make sure that all the dependencies
of the experiment file are available in the cluster.

While the experiment is running we can check its status by first fetching information:
``nerocli --fetch``

And then checking the status with:
``nerocli --status theanotest``

Eventually the experiment state will show as ``finished`` and the results will be
synced to the ``~/.neronet/results/theanotest`` folder.


===
GUI
===

**Installation**
As pyqt is not included with pip, it is required to be installed from package manager.
You can download QT for python with ``apt-get install python-qt4``
Make sure you have configured path correctly. You can check you current path with 
``import sys
print sys.path``

Gui is included in pip install. You can open gui by typing ``nerogui``

**Specify clusters**
Specify clusters by writing clusters short name to cluster name field.
Write clusters address and select its type from dropdown menu and hit add cluster to add it.


**Specify experiments**
Specify experiments by pressing "Add experiment"
A dialog should open. Navigate to the folder where your experiment folder is (the one containing config.yaml) and hit open.
Table with experiment will update if the importing was successful.

You can also drag and drop multiple folders to the NeroGUI window to add them.


**Submit experiments**

You can submit experiments by selecting experiment and folder and hitting submit button.

**Submit batches of experiments**

You can select multiple experiments by holding ctrl and pressing every experiment you want to send.
After selecting the experiments, choose cluster and hit submit.

**Experiment status report**

Selecting experiment will update log view with the information accosiated with experiment.

**Cluster status report**

Selecting experiment will update log view with the information accosiated with cluster.

**Accessing status folder**

You can get into the folder where experiment is defined by double clicking experiment.

**Collection status report**

Hit refresh to update status(es) of the experiment(s).

**Deleting experiments**

You can delte experiments by selecting experiment(s) and pressing delete key

**manipulating experiments table**

Right clicking will open menu where you can select parameters which you want to view.
By pressing headers you can sort your experiments.

**Plotting experiments**

You can plot some function of your experiment by pressing the experiment and selecting plots in plot-tab.

**Create new experiment**

Navigate to experiment tab and type command you wish to run your experiment f.ex "python test.py x y". Program will create you a template config.yaml.

**Duplicate experiment**

Select experiment and press duplicate buton in experiment-tab.

**CLI**

**Installation**

Before installing neronet check that you have Python 3.5 installed on your local machine and the clusters.

Download neronet folder
and open clusters.yaml in your favorite text editor.
Specify your initial cluster setup by using the following format:

The specification of a cluster must start with the user-specified cluster-id 
on a separate line. The following lines containing the cluster's information
must be indented and contain at least the following attributes:
ssh_address: (f.ex  triton.aalto.fi) and type: (either 'unmanaged' or 'slurm').
Additionally, it is possible to specify the maximum queue with the attribute
queue_max:
Example:

```
triton:
  ssh_address: triton.aalto.fi
  type: slurm  
  default_log_path:
  queue_max: 20
gpu1:
  ssh_address: gpu1
  type: unmanaged
  libraries, hardware
gpu2:
  ssh_address: gpu1
  type: unmanaged
  libraries, hardware
gpu: (gpu1, gpu2)
```

After that open preferences.yaml and fill in your preferences using the following format.

```
name: Pyry Takala
email: pyry.takala@gmail.com
(library versions, filetypes)
logoutput: stdout

```

Then start neronet. The program will notify you if the installation failed. 

*Start neronet*

Neronet CLI starts by running neroman.py on the command line.
```
python3.5 neroman.py
```

**Specify clusters**

All the manual updates done to clusters.yaml file are automatically configured to
neronet when the program starts. Additionally clusters can be added via command line.
Neronet supports slurm clusters and unmanaged nodes.

```
Usage: neroman --cluster ID SSH_ADDRESS TYPE
Example: neroman --cluster triton triton.cs.hut.fi slurm

```
ID is a user defined id of the cluster
SSH_ADDRESS is the ssh address of the cluster
TYPE is either slurm or unmanaged

**Specify experiments**
The following command configures an experiment with Neronet
and adds it to experiment queue

```
Usage: neroman --experiment FOLDER
Example: neroman --experiment ~/experiments/lang_exp
```
Experiment folders must include a YAML config file named `config.yaml` of
the following format: (Experiment ids must be unique)

```
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
		variablename:
		killvalue:
		comparator: >/</=
		when: immediately/after specific interval/after being run x times
		action: (kill, warn, email)
	experiment_Id: lang_exp3
		parameters:
			hyperparamz: 2
	parameter_format: '--hyperparamx %s{hyperparamx} %hyperparamy

experiment_Id: lang_exp2
	run_command_prefix: python2
	main_code_file: main2.py
	parameters:
	    hyperparamx: kh
	    hyperparamy: nyt
	    data_file: data/2.txt
	    hyperparamz: 400
	parameter_format: '--hyperparamx %s{hyperparamx} %hyperparamy
```

**Delete Experiments**

The following command deletes a specified experiment from the experiment queue.

```
neroman --delexp EXPERIMENT_ID
neroman --delexp FOLDER

```

**Submit experiments and batches of experiments**

To get info on clusters before submitting experiments type the following command:
neroman --status clusters


```
Usage: neroman --submit CLUSTER_ID EXPERIMENT_ID
Example: neroman --submit triton lang_exp3
```

Using 'any' as CLUSTER_ID will divide the work and submit it to all free clusters.
Using 'all' as EXPERIMENT_ID will submit all specified but not submitted
experiments.

```
Example: neroman --submit any EXPERIMENT_ID

```

Tasks can be submitted also by logical arguments:

```
Usage: neroman --submit CLUSTER_ID ARGUMENT

#Specify an experiment and submit it instantly
Example: neroman --submit triton ~/experiments/lang_exp x

#Submit all experiments that were specified yesterday
Example: neroman --submit triton 'tmod>yesterday'

#Submit all that have a specified parameter
Example: neroman --submit triton 'params=*data/1.txt* 

#Submit all specified, but not submitted experiments
Example: neroman --submit any all
```

**Monitoring log output**

```
Usage: neroman --monitor EXPERIMENT_ID
Example: neroman --monitor lang_exp3

```
The output will be of the following format:

Cluster
Starting time
Log output

**Status report**

The status command gives status information regarding configurations and any
specified clusters and experiments.

```
Usage: neroman --status [ARGS]
```

ARGS can refer to experiment or cluster IDs, or be collection specifiers.

```
Example: neroman --status # Overall status information
(experiment summary, experiments running, queue)

Example: neroman --status lang_exp3 # experiment status
(parameters, running/queue, time (specified, set to run, finished), final output)

Example: neroman --status 'tsub>yesterday' # collection status
(the list of experiments in the given collection and their statuses(not running/running/finished))

Example: neroman --status queue # all the experiments in the queue
(the list of experiments in the queue and specification times)

Example: neroman --status triton # cluster status
(the list of experiments running and their start times)

Example: neroman --status clusters # all cluster's statuses
```

**Backup**

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


==================
Neronet User Guide
==================

Contents
--------


- Contents
- Introduction
- Installation
- Command Line Interface:
    - Using Neronet CLI
    - Specifying and configuring experiments
    - Deleting defined experiments
    - Submitting experiments and batches of experiments to computing clusters
    - Specifying clusters
    - Monitoring log output
    - Status report
- GUI:
    - Starting Neronet GUI
    - Specifying and configuring experiments
    - Deleting defined experiments from Neronet
    - Submitting experiments and batches of experiments to computing clusters
    - Specifying clusters
    - Monitoring log output
    - Status report
- Advanced Functionalities
    - Output processing
    - Auto termination
    - Plotting output
- Example experiment

Introduction
------------

Neronet is a python-based, framework agnostic tool for computational
researchers that is made to enable easy

- batch submission of experiment jobs to computing clusters
- management of experiment queues
- monitoring of logs and parameter values for ongoing experiments
- access to experiment information during and after the run
- configurable notifications on experiment state and progress
- configurable criteria for experiment autotermination
- logging of experiment history

Neronet can be used either via command-line interface or via GUI.


Installation
------------

All components of the neronet application, including both the parts run in
clusters and the parts run in the researcher's local machine are implemented
using python 2.7, so before installation please make sure that the correct
version of python is installed on your local machine and on the computing
clusters you intend to be use. Using other python versions may cause
complications and is therefore not recommended. Then download neronet folder
and proceed by setting up your initial cluster setup and setting up your
preferences.

**1. Pip installation**

Start by running the command below on the command line of your local machine.
Note: python 2.7 is required.
:: 
  sudo pip install neronet

The command will load all components related to neronet and install them to
the system. It will also create the folder ``~/.neronet`` that contain your
preferences and cluster setup. Proceed by opening the folder and then defining
your initial cluster setup and preferences in the respective files.

**2. Setting up the initial cluster setup:**

.. IMPROVEMENTS: Should this be included? Do the user really want to manually
   modify the files?

Open ``.neronet/clusters.yaml`` file using your favorite text editor and fill
in the following information.

The format of ``clusters.yaml`` is as follows. From here on out we will
explain the formats of important files by first showing an example file and
then explaining the important points.

*Example:*

.. code:: yaml

    clusters:
        triton:
            ssh_address: triton.aalto.fi
            type: slurm
            hard_disk_space: 1000GB
        gpu1:
            ssh_address: gpu1
            type: unmanaged
        gpu2:
            ssh_address: gpu2
            type: unmanaged       
    groups:
        gpu: [gpu1, gpu2]

The specification of a cluster must start with the user-specified cluster-id
on a separate line. The following lines containing the cluster's information
must be indented and contain at least the following attributes: ssh_address:
(f.ex  triton.aalto.fi) and type: (either 'unmanaged' or 'slurm'). If the
cluster uses Simple Linux Utility for Resource Management (SLURM), its type is
'slurm', otherwise use 'unmanaged'.

Additionally, it is possible to specify optional information on the cluster
such as the hard disk space for the cluster. Although these are purely for the
user and are not used internally.

It is also possible to group some of your clusters or unmanaged nodes under a
single virtual cluster name using the following format: GROUP_ID: [NODE_ID,
NODE_ID, ...] (f.ex 'gpu: [gpu1, gpu2]' in the example above). Then later on
you can submit your experiments to that virtual cluster name and let neronet
automatically divide the work between the actual nodes.

**3. Setting up personal information and preferences:**

Open the file ``.neronet/preferences.yaml`` and fill in your name, email and
default cluster using the following format.

*Example:*

.. code:: yaml

    name: John Doe
    email: john.doe@gmail.com
    default_cluster: triton

If you followed the instructions, your neronet application should be ready to
run now. Proceed by starting neronet. The program will notify you if the
installation failed for one reason or another.

======================
Command Line Interface
======================

Using Neronet CLI
--------------------

.. IMPROVEMENTS: Should this be removed?

To start your Neronet CLI application, run nerocli on your local machine's
command line.
:: 
  nerocli --status


Specifying clusters
-------------------

You can specify clusters either via command line or by manually updating the
``clusters.yaml file.`` See the section *Installation* for more information on
the format when updating the clusters.yaml file manually.
:: 
  Usage: nerocli --addnode ID TYPE SSH_ADDRESS
  Example: nerocli --addnode triton slurm triton.cs.hut.fi

ID is a user defined id of the cluster, SSH_ADDRESS is the ssh address of the
cluster, TYPE is either 'slurm' or 'unmanaged'

The information given via CLI is then automatically updated to clusters.yaml.
If you want to save other information about a specific cluster besides the
cluster's address, name and type, you must manually write them to the
clusters.yaml file.


Specifying and configuring experiments
--------------------------------------

Neronet supports experiments written using any programming language or
framework as long as the experiments are runnable with a command of the format
'RUN_COMMAND-PREFIX CODE_FILE PARAMETERS', f.ex. 'python2.7 main.py 1 2 3 4
file.txt'

Start by writing your experiment code and save all experiments you deem
somehow related to a single folder. Then include a YAML configuration file in
your folder and name it 'config.yaml'. It is also possible to create the YAML
configuration file template with the following command:
:: 
  Usage: nerocli --template EXP_ID RUN_COMMAND-PREFIX CODE_FILE PARAMETERS
  Example: nerocli --template theanotest python theanotest.py N feats training_steps

In the configuration file you are to specify all the different experiments you
want to run using the following format. Please read this section carefully for
it contains plenty of important information.

*Example:*

.. code:: yaml

    collection: lang_exp
    run_command_prefix: python3
    main_code_file: main.py
    outputs: stdout
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


- The information on the config.yaml file is divided to blocks that have the
  same indentation.

- Each experiment specification must begin with a row containing the
  experiment id (f.ex in the example above three experiments are specified:
  lang_exp1, lang_exp2 and lang_exp3) and be followed by a block containing all
  the experiment's attributes. Do not use the reserved words, list of which can
  be found at the end of this section. The experiment ids must be unique within
  the same config file.

- Each different experiment specification must have the following attributes
    
    - main_code_file: The path to the code file that is to be run when
      executing the experiment

    - run_command_prefix: The prefix of the run command f.ex 'python2'
    
    - outputs: The location to which the log output of the experiment is to be
      written. Can be either stdout or a file path.
    
    - parameters: This attribute is followed by a block containing all the
      unique parameters of this specific experiment. Parameter names can be
      arbitrary.
    
    - parameter_format: Specifies the order in which the parameters are given
      to the experiment code file in the form of a string. Write the attribute
      value within single quotes. Parameter names written within braces will be
      replaced by their values defined in the *parameters* section. F.ex in the
      example above lang_exp2 --parameter_format defines a parameter string 'kh
      nyt data/2.txt 400'. You can escape braces and special characters with
      backslashes in case your parameter names contain braces.
    
    - Your experiments should be runnable with a command of the form
      'RUN_COMMAND_PREFIX MAIN_CODE_FILE PARAMETER_STRING' F.ex in the example
      above lang_exp2 must be runnable with the command 'python2 main2.py kh nyt
      data/2.txt 400'**

- Additionally, if you want neronet to autoterminate an experiment or give you
  a warning under certain circumstances you can use the conditions-attribute.
  Neronet supports warnings and autotermination based on a variable exceeding,
  falling below or reaching a predetermined value. The conditions-attribute must
  be followed by a block containing the specifications of the conditions and
  actions to perform

    - Start by giving a unique ID to your condition. f.ex in the example above
      'lang_exp1' has two conditions set: 'error_rate_over_50' and
      'error_rate_over_35'. Do not use the reserved words, list of which can be
      found at the end of this section. Then specify the following attributes on
      the following block.
    
    - variablename: This is the name of the variable you want to monitor
    
    - killvalue: This is the value to which you want neronet to compare the
      monitored variable
    
    - comparator: Either 'gt' (greater that), 'lt' (less than), 'eq' (equal
      to), 'geq' (greater than or equal to) or 'leq' (less than or equal to).
      Use 'gt' if you want a warning when the value of the variable monitored
      exceeds killvalue, 'lt' if you want a warning when the variable falls
      below killvalue and 'eq' if you want a warning when the variable reaches
      killvalue.
    
    - when: The value of this attribute can be either 'immediately' or 'time
      MINUTES' where MINUTES is the time interval in minutes after which the
      warning condition is checked and action performed.
    
    - action: Specifies what you want neronet to do when the warning condition
      is fulfilled. The value of this attribute is either 'kill' (if you want
      the experiment to be terminated when the warning condition is fulfilled)
      or 'warn' (if you want to see a warning message when the condition is
      fullfilled)
    
    - The log output from the experiment code must contain rows of the format:
      'VARIABLENAME VALUE'. So that neronet is able to follow the variable
      values. F.ex. in the example above the log output of lang_exp1 must
      contain rows of the form 'error_rate 24.3334', 'error_rate 49',
      'error_rate 67.01', etc... The row must not contain anything else.

- If multiple experiments have the same attribute values, it is not necessary
  to re-write every attribute for every experiment. The experiments defined in
  inner blocks automatically inherit all the attribute values specified in outer
  blocks. For example in the example above 'lang_exp1' and 'lang_exp2' inherit
  the run_command_prefix, main_code_file and outputs values from the outmost
  block and lang_exp3 inherits all the parameter values from lang_exp1. If you
  don't want to inherit a specific value, just specify it again in the inner
  block and it is automatically overwritten. For example in the example above
  lang_exp3 uses different hyperparamz and parameter_format values than its
  parent lang_exp1.

- If you place multiple parameter values within brackets and separated by a
  comma (like in the example above lang_exp1 -- hyperparamx: [1,2,34,20])Neronet
  will automatically generate different experiments for each value specified
  within brackets. (f.ex lang_exp1 would be run with the parameters '1 2
  data/1.txt 2', '2 2 data/1.txt 2', '34 2 data/1.txt 2' and '20 2 data/1.txt
  2')

After your experiment folder contains the config file of the correct format
and all the code and parameter files, you can then submit the folder to your
Neronet application with the following command.
:: 
  Usage: nerocli --addexp FOLDER
  Example: nerocli --addexp ~/experiments/lang_exp

**Reserved Words:**
:: 
  experiment_id
  run_command_prefix
  main_code_file
  parameters
  parameter_format
  outputs
  output_line_processor
  output_file_processor
  plot
  collection
  required_files
  conditions
  custom_msg
  path
  warning
  variablename
  killvalue
  comparator
  when
  action

Deleting defined experiments
----------------------------

To delete a specified experiment from your Neronet application's database you
can use the following command.
:: 
  nerocli --delexp EXPERIMENT_ID

EXPERIMENT_ID is the 'ID' attribute defined on the topmost row of the
experiment folder's config.yaml. Alternatively, if you only want to delete a
certain experiment within a folder, you can use the format 'ID/experiment_Id'
(see *specifying experiments* to find out what these attributes are). Commands
of the format 'delete ID/experiment_Id' don't affect the experiment's children
or parents.

Using the command above doesn't delete the experiment folder or any files
within it. It only removes the experiment's information from Neronet's
database. It also doesn't affect the children of the experiment.


Submitting experiments to computing clusters
--------------------------------------------

The following command will submit an experiment to a specified cluster.
:: 
  Usage: nerocli --submit EXPERIMENT_ID CLUSTER_ID 
    Example: nerocli --submit lang_exp triton 


EXPERIMENT_ID is the name of the experiment you are about to submit.

CLUSTER_ID can be any cluster id or cluster group id specified in the
clusters.yaml file or via CLI. If you have specified a default cluster in
preferences.yaml (see *Installation*), you can leave CLUSTER_ID blank to
automatically submit your experiments to the specified default cluster. F.ex
'submit lang_exp'.


Fetching data about submitted experiments:
------------------------------------------

To see the current state of the submitted experiments it is necessary to first
fetch the data from clusters. In Neronet CLI this is done by typing the
following command:
:: 
  nerocli --fetch

After that you can see the current state of your experiments by typing:
:: 
  nerocli --status
    


Status report
-------------

The status command gives status information regarding configurations and any
specified clusters and experiments.
:: 
  Usage: nerocli --status [ARGS]

ARGS can refer to experiment or cluster IDs, or be collection specifiers.

*Overall status:*
:: 
  nerocli --status

The command above will print the overall status information. That is, printing
the number of experiments with each of the different experiment states, the
list of defined clusters and their current states and finally the list of
experiments and their current states.

*Experiment status:*
:: 
  nerocli --status lang_exp3

*Cluster status:*
:: 
  Usage: nerocli --status CLUSTER_ID
  Example nerocli --status triton

=== GUI ===

**Installation** 

As pyqt is not included with pip, it is required to be installed from package
manager.  You can download QT for python with ``apt-get install python-qt4``
Make sure you have configured path correctly. You can check you current path
with ``import sys print sys.path``

Gui is included in pip install. You can open gui with ``nerogui``

**Specify clusters** 

Specify clusters by writing clusters short name to cluster name field.  Write
clusters address and select its type from dropdown menu and hit add cluster to
add it.


**Specify experiments** 

Specify experiments by pressing "Add experiment" A dialog should open.
Navigate to the folder where your experiment folder is (the one containing
config.yaml) and hit open.  Table with experiment will update if the importing
was successful.

You can also drag and drop multiple folders to the NeroGUI window to add them.


**Submit experiments**

You can submit experiments by selecting experiment and folder and hitting
submit button.

**Submit batches of experiments**

You can select multiple experiments by holding ctrl and pressing every
experiment you want to send.  After selecting the experiments, choose cluster
and hit submit.

**Experiment status report**

Selecting experiment will update log view with the information accosiated with
experiment.

**Cluster status report**

Selecting experiment will update log view with the information accosiated with
cluster.

**Accessing status folder**

You can get into the folder where experiment is defined by double clicking
experiment.

**Collection status report**

Hit refresh to update status(es) of the experiment(s).

**Deleting experiments**

You can delte experiments by selecting experiment(s) and pressing delete key

**manipulating experiments table**

Right clicking will open menu where you can select parameters which you want
to view.  By pressing headers you can sort your experiments.

**Plotting experiments**

You can plot some function of your experiment by pressing the experiment and
selecting plots in plot-tab.

**Create new experiment**

Navigate to experiment tab and type command you wish to run your experiment
f.ex "python test.py x y". Program will create you a template config.yaml.

**Duplicate experiment**

Select experiment and press duplicate buton in experiment-tab.

========================
Advanced functionalities
========================

Output processing
-----------------

To allow Neronet to undestand your experiments output you must define output
processing functions for neronet. These are defined in the ``config.yaml`` file 
for the experiment. There are two different types of output processing
functions you can define according to your output file format. 

The first one is output line processor which receives a line of output file as
input and outputs the line interpeted as a dict.

It is defined in config.yaml as such:

*config.yaml*

.. code:: yaml

    output_line_processor:
        output_file_name: module_name function_name other_arguments

- For each output file you want to be understood this way you should define a
  seperate output line processor
- The other arguments are defined as a string separated with spaces
- ``output_file_name`` must be a output file defined in the experiment outputs
- ``module_name`` refers to the module where you specify the output reading
  functions
- ``function_name`` refers to the name of the output line processing function
- ``other_arguments`` are other arguments you would want Neronet to pass to your
  function. Other arguments can also contain strings of characters with spaces
  by using quotes: "I am a string passed as an argument".

The other one is output file processor which recieves the filename of the
output file as input and outputs the file interpeted as a dict. Its definition
in the ``config.yaml`` doesn't differ from the output line processors, but
``output_line_processor`` is replaced with ``output_file_processor``.

These functions should follow the following format when defined in the module.

*module*

.. code:: python

    def some_output_line_reader(output_line, *optional_args):
        #Process optional arguments
        ...
        #Process the line data
        ...
        #Map the line data into dictionary so that neroman can understand it
        ...
        return output_dict

    def some_output_file_reader(output_file, *optional_args):
        #Process optional arguments
        ...
        #Read and process the output file
        ...
        #Map the line data into dictionary so that neroman can understand it
        ...
        return output_dict

- The users are free to name the functions and parameters in any way they see
  fit.
- ``output_line`` is a string containing a line of the output.
- ``output_file`` is a file object returned by open.
- ``optional_args`` are other arguments the user wants the function to
  receive. You can also name give names to the other optional arguments, but
  then you must take special care that output processors receive the correct
  amount of arguments.

The user should take special care that the functions are valid python and can
actually used to read the user input. If the user functions fail at any point
Neronet cannot use the functions and will give warnings to the user.

Auto termination
----------------

Plotting output 
---------------

To allow Neronet to plot your output you must define plotting functions for
your outputs. These are defined in the ``config.yaml`` for the experiment.

It is defined in config.yaml as such:

*config.yaml*

.. code:: yaml

    plot:
        plot_name: module_name function_name output_filenames other_arguments

- Each plot you want to be generated should be defined on their own lines
  under the ``plot`` line.
- ``plot_name`` should be the name of the plot generated.
- ``module_name`` refers to the module where you specify the plotting
  function
- ``function_name`` refers to the name of the plotting functions
- ``output_filenames`` specifies the output file used for plotting. The output
  file should have a output processing function defined so that Neronet can give
  them to the plotting function. Either line or file processer works.
- ``other_arguments`` are other arguments you would want Neronet to pass to
  your function. To allow your plotting function to use your experiment output
  you can use variables defined in the output dicts. Each argument that is
  contained in the output is replaced with a tuple containing the name of the
  variable as the first element and the data of the output pertaining to that
  variable as the second element. Other arguments can also contain strings of
  characters with spaces by using quotes: "I am a string passed as an argument".

These functions should follow the following format when defined in the module.

*module*

.. code:: python

    def plotting_function(plot_name, feedback, save_image, *optional_args):
        #Process optional arguments
        ...
        #Process the line data
        ...
        #Map the line data into dictionary so that neroman can understand it
        ...
        return feedback

- The users are free to name the functions and parameters in any way they see
  fit.
- ``plot_name`` is a string containing the name of the plot to be saved.
- ``feedback`` is a special variable that can be used for combining plots. It
  doesn't need to be used and is set to None by Neronet when normally plotting.
- ``save_image`` is also a special variable that can be used for combining
  plots. It doesn't need to be used and is set to None by Neronet when normally
  plotting.
- ``optional_args`` are other arguments the user wants the function to
  receive. You can also name give names to the other optional arguments, but
  then you must take special care that output processors receive the correct
  amount of arguments.

The user should take special care that the functions are valid python and can
actually used to read the user input. If the user functions fail at any point
Neronet cannot use the functions and will give warnings to the user.

Example experiment 
==================

Assume we have folder ``~/example_experiment`` which contains an experiment named
``experiment.py`` and we want to submit it to ``my.cluster.org`` to be run there.
We proceed as follows:

Define a cluster where the experiment is to be run: ``nerocli --addnode my_cluster my.cluster.org``

Neronet requires some information about each experiment, which is why we
create the file ``~/example_experiment/config.yaml`` with the following content

.. code:: yaml

    run_command_prefix: 'python' 
    main_code_file: 'experiment.py' 
    example1: 
        parameters: 
            x: 2
            y: 4
        parameters_format: '{x} {y}' 

Now we let Neronet know about the experiment by registering it: ``nerocli --addexp ~/example_experiment``

Finally, we submit the experiment to be run in the cluster: ``nerocli --submit example1 my_cluster``

Before submitting of course you need to make sure that all the dependencies of
the experiment file are available in the cluster.

While the experiment is running, we can check its status with: ``nerocli --status``

Eventually the experiment will show as ``finished`` and the results will be
automatically synced to the ``~/.neronet/results/theanotest`` folder.

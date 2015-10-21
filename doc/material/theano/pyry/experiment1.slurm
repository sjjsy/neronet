#!/bin/bash 

#SBATCH -J LM_miuc
#SBATCH -o miuc_%j.out
#SBATCH -p gpu
#SBATCH --gres=gpu:2
#SBATCH --mem-per-cpu=16000
#SBATCH -t 1-23:59:59

module load python-env
cd ../owlet
echo "Starting the run"

## list the commands you wish to run
python lang_experiment.py
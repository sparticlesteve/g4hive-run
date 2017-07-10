#!/bin/bash

# This script is my attempt to update and translate Charles's run_batch_smap
# c-shell script to bash

nProc=0
nEvent=500
if [ $# -eq 3 ]; then
    nEvent=$3
    nProc=$2
    nThread=$1
elif [ $# -eq 2 ]; then
    nProc=$2
    nThread=$1
elif [ $# -eq 1 ]; then
    nThread=$1
else
    echo "usage: $0 nThreads [nProcs] [nEvent]"
    exit 1
fi

startDir=$PWD

# Run directory
runDir=/tmp/$USER/results_`date +"%s%N"`
mkdir -p $runDir && cd $runDir

date
echo "Launching $nThread threads, $nProc procs, $nEvent events"
echo "Started from directory $startDir"
echo "Running in directory $runDir"

# Launch athena
jobOpts=$startDir/G4HiveExOpts.py
athena.py --threads=$nThread --nproc=$nProc -c "evtMax=$nEvent" $jobOpts

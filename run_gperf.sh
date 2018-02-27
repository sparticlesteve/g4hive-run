#!/bin/bash

# This script uses GPerfTools to profile G4Hive.

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

# Abort on error
set -e

startDir=$PWD

# Run directory
runDir=/tmp/$USER/results_`date +"%s%N"`
mkdir $runDir && cd $runDir

# Output log files
configStr="${nThread}_${nProc}_${nEvent}"
logFile="log.${configStr}.log"
profFile="prof.${configStr}.profile"

echo "Launching $nThread threads, $nProc procs, $nEvent events"
echo "Started from directory $startDir"
echo "Running in directory $runDir"
echo "log to $logFile"

# Command line options
jobOpts=$startDir/jobOptions.G4AtlasMT.py
commands="evtMax=$nEvent"
profOpts="--profilerMode eventLoop --profilerInitEvent 2 --profilerOutput $profFile"
concurrencyOpts="--threads=$nThread --nproc=$nProc"

# Launch athena
gathena $profOpts $concurrencyOpts -c "$commands" $jobOpts &> $logFile

grep "leaving with code" $logFile

# Move outputs to results dir
resultsDir=$startDir/results_gperf
echo "Moving outputs to $resultsDir"
mkdir -p $resultsDir
mv $logFile $resultsDir/
mv $profFile $resultsDir/
rm -rf $runDir

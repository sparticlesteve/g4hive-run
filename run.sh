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

# Abort on error
set -e

startDir=$PWD

# Run directory
runDir=/tmp/$USER/results_`date +"%s%N"`
mkdir $runDir && cd $runDir

# Output log files
configStr="${nThread}_${nProc}_${nEvent}"
logFile="log.$configStr.log"
memFile="mem.$configStr.csv"
timeFile="timeline.$configStr.log"

echo "Launching $nThread threads, $nProc procs, $nEvent events"
echo "Started from directory $startDir"
echo "Running in directory $runDir"
echo "log to $logFile"
echo "mem to $memFile"
echo "timeline to $timeFile"

# Launch athena
startTime=$(date +"%s%N")
jobOpts=$startDir/G4HiveExOpts.py
athena.py --threads=$nThread --nproc=$nProc -c "evtMax=$nEvent" $jobOpts &> $logFile &
# Launch memory monitor
$startDir/MemoryMonitor --pid $! --filename $memFile --interval 1000
endTime=$(date "+%s%N")

grep "leaving with code" $logFile

# Finalize timeline
echo $startTime > $timeFile
cat timeline.csv >> $timeFile
echo $endTime >> $timeFile

# Move outputs to results dir
resultsDir=$startDir/results
echo "Moving outputs to $resultsDir"
mkdir -p $resultsDir
mv $logFile $resultsDir/
mv $memFile $resultsDir/
mv $timeFile $resultsDir/
rm -rf $runDir

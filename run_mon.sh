#!/bin/bash

# This script is my attempt to update and translate Charles's run_batch_smap
# c-shell script to bash

# Default parameters
nThread=1
nProc=0
nEvent=500

if [ $# -lt 1 ]; then
    echo "usage: $0 resultsDir [nThreads=$nThread] [nProcs=$nProc] [nEvent=$nEvent]"
    exit 1
fi

resultsDir=$1

if [ $# -ge 2 ]; then nThread=$2; fi
if [ $# -ge 3 ]; then nProc=$3; fi
if [ $# -ge 4 ]; then nEvent=$4; fi

scriptDir=$(dirname "$(readlink -f "$0")")
runDir=$(mktemp -d)
cd $runDir

# Output log files
configStr="${nThread}_${nProc}_${nEvent}"
logFile="log.$configStr.log"
memFile="mem.$configStr.csv"
timeFile="timeline.$configStr.log"

date
echo "Launching $nThread threads, $nProc procs, $nEvent events"
echo "Running scripts from $scriptDir"
echo "Running in directory $runDir"
echo "log to $logFile"
echo "mem to $memFile"
echo "timeline to $timeFile"

# Launch athena
startTime=$(date +"%s%N")
jobOpts=$scriptDir/G4HiveExOpts.py
athena.py --threads=$nThread --nproc=$nProc -c "evtMax=$nEvent" $jobOpts &> $logFile &
# Launch memory monitor
$scriptDir/MemoryMonitor --pid $! --filename $memFile --interval 1000
endTime=$(date "+%s%N")

grep "leaving with code" $logFile

# Finalize timeline
echo $startTime > $timeFile
if [ $nProc -eq 0 ]; then
    cat timeline.csv >> $timeFile
else
    # For MP, we concatenate the timelines from each worker
    for workerTimeFile in athenaMP_workers/worker_*/timeline.csv; do
        cat $workerTimeFile >> $timeFile
    done
fi
echo $endTime >> $timeFile

# Move outputs to results dir
echo "Moving outputs to $resultsDir"
mkdir -p $resultsDir
mv $logFile $resultsDir/
mv $memFile $resultsDir/
mv $timeFile $resultsDir/

# Cleanup
rm g4hive.hits.pool.root

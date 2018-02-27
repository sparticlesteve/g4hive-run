#!/bin/bash

#
# This script will run G4AtlasMT with a specified number of threads and events
# on a specified input file.
#
# It also runs the MemoryMonitor alongside athena to collect runtime data.
#

# Default config
nEvent=500
nThread=1
inputFile=/project/projectdirs/atlas/sfarrell/evnt/mc15_13TeV.424000.ParticleGun_single_mu_Pt100.evgen.EVNT.e3580/EVNT.04922446._000063.pool.root.1
resultsDir=$PWD/results

#if [ $# -lt 1 ]; then
#    echo "usage: $0 resultsDir [nThreads=$nThread] [nProcs=$nProc] [nEvent=$nEvent]"
#    exit 1
#fi
#resultsDir=$1
#if [ $# -ge 2 ]; then nThread=$2; fi
#if [ $# -ge 3 ]; then nProc=$3; fi
#if [ $# -ge 4 ]; then nEvent=$4; fi

# Parse command line options
while getopts ":hn:t:i:o:" opt; do
    case $opt in
        h)
            echo "Usage: $0 -t nThreads -n nEvents -i inputFile -o outputDir"
            exit 0
            ;;
        n)
            nEvent=$OPTARG
            ;;
        t)
            nThread=$OPTARG
            ;;
        i)
            inputFile=$OPTARG
            ;;
        o)
            resultsDir=$OPTARG
            ;;
        \?)
            echo "Invalid option: $OPTARG" 1>&2
            exit 1
    esac
done

scriptDir=$(dirname "$(readlink -f "$0")")
runDir=$(mktemp -d)
cd $runDir

# Output log files
configStr="${nThread}_${nEvent}"
logFile="log.$configStr.log"
memFile="mem.$configStr.csv"
#timeFile="timeline.$configStr.log"

date
echo "Launching $nThread threads, $nEvent events"
echo "Running scripts from $scriptDir"
echo "Running in directory $runDir"
echo "log to $logFile"
echo "mem to $memFile"
#echo "timeline to $timeFile"

# Launch athena
startTime=$(date +"%s%N")
jobOpts=$scriptDir/jobOptions.G4AtlasMT.py
athena.py --threads=$nThread --evtMax $nEvent --filesInput=$inputFile $jobOpts &> $logFile &
# Launch memory monitor
$scriptDir/MemoryMonitor --pid $! --filename $memFile --interval 1000
endTime=$(date "+%s%N")

grep "leaving with code" $logFile

# Finalize timeline
#echo $startTime > $timeFile
#cat timeline.csv >> $timeFile
#echo $endTime >> $timeFile

# Move outputs to results dir
echo "Moving outputs to $resultsDir"
mkdir -p $resultsDir
mv $logFile $resultsDir/
mv $memFile $resultsDir/
mv $timeFile $resultsDir/

# Cleanup
rm g4atlas.hits.pool.root

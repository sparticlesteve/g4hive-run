#!/bin/bash

#
# This script will run G4AtlasMT with a specified number of threads and events
# on a specified input file.
#
# This script is in development with more command line option features.
#

# Default config
nEvent=500
nThread=1
inputFile=/project/projectdirs/atlas/sfarrell/evnt/mc15_13TeV.424000.ParticleGun_single_mu_Pt100.evgen.EVNT.e3580/EVNT.04922446._000063.pool.root.1

# Parse command line options
while getopts ":hn:t:i:" opt; do
    case $opt in
        h)
            echo "Usage: $0 -t nThreads -n nEvents -i inputFile"
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
        \?)
            echo "Invalid option: $OPTARG" 1>&2
            exit 1
    esac
done

startDir=$PWD

# Run directory
runDir=/tmp/$USER/results_`date +"%s%N"`
mkdir -p $runDir && cd $runDir

date
echo "Launching $nThread threads, $nEvent events"
echo "Input file: $inputFile"
echo "Started from directory $startDir"
echo "Running in directory $runDir"

# Launch athena
jobOpts=$startDir/jobOptions.G4AtlasMT.py
athena.py --threads=$nThread --evtMax $nEvent --filesInput=$inputFile $jobOpts

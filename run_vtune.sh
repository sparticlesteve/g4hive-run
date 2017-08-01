#!/bin/bash

# Results directory
resDir=$SCRATCH/g4hive/vtune/r001ge

# Advanced hotspots configuration
#vtuneOpts="-collect advanced-hotspots -start-paused"

# General exploration configuration
vtuneOpts="-collect general-exploration -r $resDir -start-paused -mrte-mode=native -target-duration-type=medium -data-limit=0"

# HPC performance configuration
#vtuneOpts="-collect hpc-performance -knob collect-memory-bandwidth=true -start-paused -mrte-mode=native -target-duration-type=medium -data-limit=0"

# Athena configuration; change as needed.
athenaOpts="--threads=32 --stdcmalloc -c \"evtMax=160;vtune=True\" ./G4HiveExOpts.py"
#athenaOpts="--threads=1 --stdcmalloc -c \"evtMax=5;vtune=True\" ./G4HiveExOpts.py"

# Run it
athena=`which athena.py`
set -x
amplxe-cl $vtuneOpts -- $athena $athenaOpts

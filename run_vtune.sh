#!/bin/bash

# Advanced hotspots configuration
#vtuneOpts="-collect advanced-hotspots -start-paused"

# General exploration configuration
#vtuneOpts="-collect general-exploration -start-paused -mrte-mode=native -target-duration-type=medium -data-limit=0"

# HPC performance configuration
vtuneOpts="-collect hpc-performance -knob collect-memory-bandwidth=true -start-paused -mrte-mode=native -target-duration-type=medium -data-limit=0"

# Athena configuration; change as needed.
athenaOpts="--threads=1 --stdcmalloc -c \"evtMax=10;vtune=True\" ./G4HiveExOpts.py"

# Run it
athena=`which athena.py`
set -x
amplxe-cl $vtuneOpts -- $athena $athenaOpts

#!/bin/bash

# Advanced hotspots configuration
#vtuneOpts="-collect advanced-hotspots -start-paused"

# General exploration configuration
#vtuneOpts="-collect general-exploration -start-paused -mrte-mode=native -target-duration-type=medium -data-limit=0"

# HPC performance configuration
vtuneOpts="-collect hpc-performance -start-paused -mrte-mode=native -target-duration-type=medium -data-limit=0"

# Athena configuration
athenaOpts="--threads=1 --stdcmalloc -c \"evtMax=10;vtune=True\" ./G4HiveExOpts.py"

# Run it
amplxe-cl $vtuneOpts -- `which athena.py` $athenaOpts

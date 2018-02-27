#!/bin/bash

# Results directory
resDir=$SCRATCH/athsim/vtune/r001ge

# Advanced hotspots configuration
#vtuneOpts="-collect advanced-hotspots -start-paused"

# General exploration configuration
vtuneOpts="-collect general-exploration -r $resDir -start-paused -mrte-mode=native -target-duration-type=medium -data-limit=0"

# HPC performance configuration
#vtuneOpts="-collect hpc-performance -knob collect-memory-bandwidth=true -start-paused -mrte-mode=native -target-duration-type=medium -data-limit=0"

# Athena configuration; change as needed.
nThread=1
nEvent=1
inputFile=/project/projectdirs/atlas/sfarrell/evnt/mc15_13TeV.424000.ParticleGun_single_mu_Pt100.evgen.EVNT.e3580/EVNT.04922446._000063.pool.root.1
athenaOpts="--threads=$nThread --evtmax=$nEvent --filesInput=$inputFile --stdcmalloc ./jobOptions.G4AtlasMT.py ./vtune.fragment.py"

# Run it
athena=`which athena.py`
set -x
amplxe-cl $vtuneOpts -- $athena $athenaOpts

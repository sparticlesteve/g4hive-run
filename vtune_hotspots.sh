#!/bin/bash

# Pass the profiler results dir as an argument
if [ $# -lt 1 ]; then
    echo "Provide vtune output"
    exit 1
fi

results=$1
rows=50

amplxe-cl -report hotspots -r $results -limit=$rows
#amplxe-cl -report hotspots -r $results -limit=$rows -column="Clockticks,Retired,CPI,Front-End Bound:Self,Bad Speculation:Self,Back-End Bound:Self"

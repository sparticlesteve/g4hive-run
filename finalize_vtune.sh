#!/bin/bash

if [ $# -lt 1 ]; then
    echo "provide results dir"
    exit 1
fi

# Use full library path for search
for dir in $(echo $LD_LIBRARY_PATH | tr ':' ' '); do
    searchStr="$searchStr -search-dir $dir"
done

amplxe-cl -finalize -r $1 $searchStr

#amplxe-cl -finalize -result-dir $1 \
#    -search-dir /project/projectdirs/atlas/sfarrell/nightly-kits/20.8.2/gcc-alt-493/x86_64-slc6-gcc49-opt/lib64 \
#    -search-dir /project/projectdirs/atlas/sfarrell/nightly-kits/20.8.2/AtlasSimulation/20.8.2/InstallArea/x86_64-slc6-gcc49-opt/lib \
#    -search-dir /project/projectdirs/atlas/sfarrell/nightly-kits/20.8.2/AtlasEvent/20.8.2/InstallArea/x86_64-slc6-gcc49-opt/lib \
#    -search-dir /project/projectdirs/atlas/sfarrell/nightly-kits/20.8.2/AtlasCore/20.8.2/InstallArea/x86_64-slc6-gcc49-opt/lib \
#    -search-dir /project/projectdirs/atlas/sfarrell/nightly-kits/20.8.2/GAUDI/v27r1p6-hive/InstallArea/x86_64-slc6-gcc49-opt/lib \
#    -search-dir /project/projectdirs/atlas/sfarrell/nightly-kits/20.8.2/LCGCMT/LCGCMT_84/InstallArea/x86_64-slc6-gcc49-opt/lib \
#    -search-dir /project/projectdirs/atlas/sfarrell/nightly-kits/20.8.2/gcc-alt-493/x86_64-slc6-gcc49-opt/lib64 \
#    -search-dir /project/projectdirs/atlas/sfarrell/nightly-kits/20.8.2/AtlasConditions/20.8.2/InstallArea/x86_64-slc6-gcc49-opt/lib \
#    -search-dir /usr/lib64 \
#    -search-dir /lib64

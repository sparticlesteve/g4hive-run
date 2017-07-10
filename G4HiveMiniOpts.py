# 
## G4HiveMiniOpts.py - an example job options for multi-threaded simulation
## in AthenaHive, simplified for Intel OpenLab performance studies.
## Run it by specifying the number of threads at the command line:
## $ athena --threads=4 ./G4HiveMiniOpts.py
#

from AthenaCommon.ConcurrencyFlags import jobproperties as jp
nThreads = jp.ConcurrencyFlags.NumThreads()
if (nThreads < 1) :
   from AthenaCommon.Logging import log as msg
   msg.fatal('numThreads must be >0. Did you set the --threads=N option?')
   sys.exit(AthenaCommon.ExitCodes.CONFIGURATION_ERROR)

# Message formatting
msgFmt = "% F%38W%S%6W%e%s%7W%R%T %0W%M"
svcMgr.MessageSvc.Format = msgFmt

# Thread pool service
from GaudiHive.GaudiHiveConf import ThreadPoolSvc
svcMgr += ThreadPoolSvc("ThreadPoolSvc")

# Algorithm resource pool
from GaudiHive.GaudiHiveConf import AlgResourcePool
svcMgr += AlgResourcePool( OutputLevel = INFO );


######################################################################################
#
## AthenaCommon flags

from AthenaCommon.AthenaCommonFlags import athenaCommonFlags
athenaCommonFlags.PoolEvgenInput = [
    '/afs/cern.ch/atlas/offline/ProdData/16.6.X/16.6.7.Y/e_E50_eta0-60.evgen.pool.root',
]

athenaCommonFlags.PoolHitsOutput = "g4hive.hits.pool.root"
athenaCommonFlags.EvtMax = 50

######################################################################################
#
## Job options for Geant4 ATLAS detector simulations
#

## Detector flags
from AthenaCommon.DetFlags import DetFlags
DetFlags.ID_setOn()
DetFlags.Calo_setOn()
DetFlags.Muon_setOff()
DetFlags.Lucid_setOff()
DetFlags.Truth_setOff()

## Global conditions tag
from AthenaCommon.GlobalFlags import jobproperties
#jobproperties.Global.ConditionsTag = "OFLCOND-MC12-SIM-00"
jobproperties.Global.ConditionsTag = "OFLCOND-RUN12-SDR-21"

## Simulation flags
from G4AtlasApps.SimFlags import simFlags
simFlags.load_atlas_flags()
simFlags.SimLayout.set_On()
simFlags.EventFilter.set_Off()
simFlags.LArParameterization = 0
simFlags.CalibrationRun.set_Off()
simFlags.MagneticField.set_Off()
simFlags.UseV2UserActions = True

# G4InitTool handles worker thread G4 infrastructure setup
svcMgr.ThreadPoolSvc.ThreadInitTools = ["G4InitTool"]

# Setup the algorithm sequence
from AthenaCommon.AlgSequence import AlgSequence
topSeq = AlgSequence()

# VTune instrumentation algorithm
if 'vtune' in dir() and vtune:
    from VTune_CCAPI.VTune_CCAPIConf import CCAPI_Alg
    topSeq += CCAPI_Alg("VTune_CCAPI", OutputLevel=DEBUG, resumeAtBeginRun=True)

# SGInputLoader is a module in SGComps that will do a typeless StoreGate read
# of data on disk, to preload it in the Whiteboard for other Alorithms to use.
# Is uses the same syntax as Algorithmic dependency declarations
from AthenaCommon import CfgMgr
topSeq += CfgMgr.SGInputLoader(OutputLevel = INFO, ShowEventDump=False)
topSeq.SGInputLoader.Load = [('McEventCollection','GEN_EVENT')]

# Add the beam effects algorithm
from AthenaCommon.CfgGetter import getAlgorithm
topSeq += getAlgorithm("BeamEffectsAlg", tryDefaultConfigurable=True)

# Add the G4 simulation service
from G4AtlasApps.PyG4Atlas import PyG4AtlasSvc
svcMgr += PyG4AtlasSvc()

# Manually declared data dependencies (for now anyway)
topSeq.G4AtlasAlg.ExtraInputs =  [('McEventCollection','BeamTruthEvent')]
topSeq.G4AtlasAlg.ExtraOutputs = [('SiHitCollection','SCT_Hits')]
topSeq.StreamHITS.ExtraInputs += topSeq.G4AtlasAlg.ExtraOutputs

# Disable all of the LAr SDs because they are not yet thread-safe
sdMaster = ToolSvc.SensitiveDetectorMasterTool
larSDs = [sd for sd in sdMaster.SensitiveDetectors if sd.name().startswith('LAr')]
for sd in larSDs: sdMaster.SensitiveDetectors.remove(sd)

# Disable alg filtering - doesn't work in multi-threading
topSeq.StreamHITS.AcceptAlgs = []

# Configure algorithm cloning.
# set algCardinality = 1 to disable cloning for all Algs.
algCardinality = jp.ConcurrencyFlags.NumThreads()
if (algCardinality != 1):
    for alg in topSeq:
        name = alg.name()
        if name in ['StreamHITS', 'VTune_CCAPI']:
            print 'Disabling cloning/cardinality for', name
            # Don't clone these algs
            alg.Cardinality = 1
            alg.IsClonable = False
        else:
            alg.Cardinality = algCardinality
            alg.IsClonable = True

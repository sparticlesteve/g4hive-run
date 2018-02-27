#
#  Copyright (C) 2002-2017 CERN for the benefit of the ATLAS collaboration
#

#
# Job options file for multi-threaded Geant4 ATLAS detector simulation.
# Run this by specifying the number of threads on the command line:
# $ athena --threads=4 G4AtlasApps/jobOptions.G4AtlasMT.py
#

from AthenaCommon.Logging import log as msg

from AthenaCommon.ConcurrencyFlags import jobproperties as jp
nThreads = jp.ConcurrencyFlags.NumThreads()
if (nThreads < 1) :
   msg.fatal('numThreads must be >0. Did you set the --threads=N option?')
   sys.exit(AthenaCommon.ExitCodes.CONFIGURATION_ERROR)

# Message stream format
msgFmt = "% F%40W%S%5W%e%s%7W%R%T %0W%M"
svcMgr.MessageSvc.Format = msgFmt

# Make the scheduler dump some information
from AthenaCommon.AlgScheduler import AlgScheduler
#AlgScheduler.ShowControlFlow( True )
#AlgScheduler.ShowDataDependencies( True )

# Thread pool service and G4 thread initialization
from GaudiHive.GaudiHiveConf import ThreadPoolSvc
svcMgr += ThreadPoolSvc("ThreadPoolSvc")
svcMgr.ThreadPoolSvc.ThreadInitTools = ["G4ThreadInitTool"]


# AthenaCommon flags
from AthenaCommon.AthenaCommonFlags import athenaCommonFlags

if len(athenaCommonFlags.FilesInput()) > 0:
    athenaCommonFlags.PoolEvgenInput = athenaCommonFlags.FilesInput()
else:
    athenaCommonFlags.PoolEvgenInput = [
        '/afs/cern.ch/atlas/offline/ProdData/15.6.11.3/mu_E200_eta0-60-10000.evgen.pool.root']
athenaCommonFlags.PoolHitsOutput = "g4atlas.hits.pool.root"
athenaCommonFlags.EvtMax = 500

# Global conditions tag
from AthenaCommon.GlobalFlags import jobproperties
jobproperties.Global.ConditionsTag = "OFLCOND-RUN12-SDR-21"

# Detector flags
from AthenaCommon.DetFlags import DetFlags
DetFlags.ID_setOn()
DetFlags.Calo_setOn()
DetFlags.Muon_setOn()
DetFlags.Lucid_setOff()
DetFlags.Truth_setOn()

# Simulation flags
from G4AtlasApps.SimFlags import simFlags
simFlags.load_atlas_flags()
# Use the default layout
simFlags.SimLayout.set_On()
# Set the EtaPhi, VertexSpread and VertexRange checks on/off
simFlags.EventFilter.set_Off()
# Set the LAr parameterization
#simFlags.LArParameterization = 2
# Magnetic field
simFlags.MagneticField.set_On()

# Debug outputs of user actions
#CfgGetter.getPublicTool('G4UA::AthenaTrackingActionTool').OutputLevel = DEBUG

include("G4AtlasApps/G4Atlas.flat.configuration.py")

# Setup the algorithm sequence
from AthenaCommon.AlgSequence import AlgSequence
topSeq = AlgSequence()

from AthenaCommon import CfgMgr
CfgMgr.SGInputLoader().Load += [('McEventCollection', 'StoreGateSvc+GEN_EVENT')]

# Add the beam effects algorithm
from AthenaCommon.CfgGetter import getAlgorithm
topSeq += getAlgorithm("BeamEffectsAlg", tryDefaultConfigurable=True)

# Add the (python) G4 simulation service.
# This will kickstart a lot of simulation setup.
topSeq += getAlgorithm("G4AtlasAlg", tryDefaultConfigurable=True)

# Explicitly specify the data-flow dependencies of G4AtlasAlg and StreamHITS.
# This is done like this because currently our VarHandles do not live in the
# algorithm but rather in Geant4 components.
topSeq.G4AtlasAlg.ExtraInputs =  [('McEventCollection','StoreGateSvc+BeamTruthEvent')]
topSeq.G4AtlasAlg.ExtraOutputs = [('SiHitCollection','StoreGateSvc+SCT_Hits')]
topSeq.StreamHITS.ExtraInputs += topSeq.G4AtlasAlg.ExtraOutputs

# Increase verbosity of the output stream
#topSeq.StreamHITS.OutputLevel = DEBUG

# Disable alg filtering - doesn't work yet in multi-threading
topSeq.StreamHITS.AcceptAlgs = []

# Override algorithm cloning settings
for alg in topSeq:
    if alg.name() != 'StreamHITS':
        alg.Cardinality = nThreads

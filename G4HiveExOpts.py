# 
## G4HiveExOpts.py - an example job options for multi-threaded simulation
## in AthenaHive. This configuration can only be run if Hive is enabled.
## Run it by specifying the number of threads at the command line:
## $ athena --threads=4 ./G4HiveExOpts.py
#

from AthenaCommon.Logging import log as msg

from AthenaCommon.ConcurrencyFlags import jobproperties as jp
nThreads = jp.ConcurrencyFlags.NumThreads()
if (nThreads < 1) :
   msg.fatal('numThreads must be >0. Did you set the --threads=N option?')
   sys.exit(AthenaCommon.ExitCodes.CONFIGURATION_ERROR)

# Message formatting
msgFmt = "% F%40W%S%6W%e%s%7W%R%T %0W%M"
svcMgr.MessageSvc.Format = msgFmt

# Thread pool service
from GaudiHive.GaudiHiveConf import ThreadPoolSvc
svcMgr += ThreadPoolSvc("ThreadPoolSvc")


######################################################################################
#
## AthenaCommon flags

from AthenaCommon.AthenaCommonFlags import athenaCommonFlags
athenaCommonFlags.PoolEvgenInput = [
    # 5 single-mu files
    #'/project/projectdirs/atlas/sfarrell/evnt/mc15_13TeV.424000.ParticleGun_single_mu_Pt100.evgen.EVNT.e3580/EVNT.04922446._000063.pool.root.1',
    #'/project/projectdirs/atlas/sfarrell/evnt/mc15_13TeV.424000.ParticleGun_single_mu_Pt100.evgen.EVNT.e3580/EVNT.04922446._000100.pool.root.1',
    #'/project/projectdirs/atlas/sfarrell/evnt/mc15_13TeV.424000.ParticleGun_single_mu_Pt100.evgen.EVNT.e3580/EVNT.04922446._000111.pool.root.1',
    #'/project/projectdirs/atlas/sfarrell/evnt/mc15_13TeV.424000.ParticleGun_single_mu_Pt100.evgen.EVNT.e3580/EVNT.04922446._000129.pool.root.1',
    #'/project/projectdirs/atlas/sfarrell/evnt/mc15_13TeV.424000.ParticleGun_single_mu_Pt100.evgen.EVNT.e3580/EVNT.04922446._000134.pool.root.1',
    #'/project/projectdirs/atlas/sfarrell/evnt/mc15_13TeV.424000.ParticleGun_single_mu_Pt100.evgen.EVNT.e3580/EVNT.04922446._000137.pool.root.1',
    #'/project/projectdirs/atlas/sfarrell/evnt/mc15_13TeV.424000.ParticleGun_single_mu_Pt100.evgen.EVNT.e3580/EVNT.04922446._000183.pool.root.1',

    # 2k TTBar events
    #'/project/projectdirs/atlas/sfarrell/evnt/mc15_13TeV.410000.PowhegPythiaEvtGen_P2012_ttbar_hdamp172p5_nonallhad.evgen.EVNT.e3698/EVNT.05192704._005477.pool.root.1',
    #'/project/projectdirs/atlas/sfarrell/evnt/mc15_13TeV.410000.PowhegPythiaEvtGen_P2012_ttbar_hdamp172p5_nonallhad.evgen.EVNT.e3698/EVNT.05192704._018877.pool.root.1',

    # 1 TTBar file
    #'/project/projectdirs/atlas/sfarrell/evnt/ttbar_muplusjets/ttbar_muplusjets-pythia6-7000.evgen.pool.root',

    # 5k Zmumu events
    #'/project/projectdirs/atlas/sfarrell/evnt/mc15_13TeV.361710.AlpgenPythiaEvtGen_P2012_ZmumuNp0.evgen.EVNT.e4721/EVNT.07352213._002022.pool.root.1',

    # 5k Ztautau events
    '/project/projectdirs/atlas/sfarrell/evnt/mc15_13TeV.361722.AlpgenPythiaEvtGen_P2012_ZtautauNp2.evgen.EVNT.e4721/EVNT.07352247._000206.pool.root.1',

    #'/afs/cern.ch/atlas/offline/ProdData/16.6.X/16.6.7.Y/ttbar_muplusjets-pythia6-7000.evgen.pool.root',
]

# Dirty way to set number of events via command line
if 'evtMax' in dir(): pass
else: evtMax = -1

# check to see if we're running hybrid mp/mt
nProc = jp.ConcurrencyFlags.NumProcs()
if (nProc > 0) :

   # For MP/Hive we need to set the chunk size
   from AthenaCommon.Logging import log as msg
   if (evtMax == -1) :
      msg.fatal('EvtMax must be >0 for hybrid configuration')
      sys.exit(AthenaCommon.ExitCodes.CONFIGURATION_ERROR)

   if ( evtMax % nProc != 0 ) :
      msg.warning('EvtMax[%s] is not divisible by nProcs[%s]: ' +
                  'MP Workers will not process all requested events',
                  evtMax, nProc)

   chunkSize = int (evtMax / nProc)
   from AthenaMP.AthenaMPFlags import jobproperties as jps
   jps.AthenaMPFlags.ChunkSize = chunkSize
   msg.info('AthenaMP workers will process %s events each', chunkSize)

athenaCommonFlags.PoolHitsOutput = "g4hive.hits.pool.root"
athenaCommonFlags.EvtMax = evtMax

######################################################################################
#
## Job options for Geant4 ATLAS detector simulations
#

# Detector flags
from AthenaCommon.DetFlags import DetFlags
DetFlags.ID_setOn()
DetFlags.Calo_setOn()
DetFlags.Muon_setOn()
DetFlags.Lucid_setOff()
DetFlags.Truth_setOn()

# Global conditions tag
from AthenaCommon.GlobalFlags import jobproperties
jobproperties.Global.ConditionsTag = "OFLCOND-RUN12-SDR-21" #"OFLCOND-MC12-SIM-00"

# Simulation flags
from G4AtlasApps.SimFlags import simFlags
simFlags.load_atlas_flags()
# Use the default layout:
simFlags.SimLayout.set_On()
# Set the EtaPhi, VertexSpread and VertexRange checks on/off
simFlags.EventFilter.set_Off()
# Set the LAr parameterization
simFlags.LArParameterization = 0
# Calorimeter calibration run settings
simFlags.CalibrationRun.set_Off()
# Magnetic field
simFlags.MagneticField.set_On()

# G4InitTool handles worker thread G4 infrastructure setup
svcMgr.ThreadPoolSvc.ThreadInitTools = ["G4InitTool"]

# Setup the algorithm sequence
from AthenaCommon.AlgSequence import AlgSequence
topSeq = AlgSequence()

# VTune instrumentation algorithm
if 'vtune' in dir() and vtune:
    from AthenaCommon.AppMgr import theApp
    from IntelProfiling.IntelProfilingConf import VTuneProfilerSvc
    svcMgr += VTuneProfilerSvc('VTuneProfilerSvc')
    theApp.CreateSvc += [ 'VTuneProfilerSvc' ]

# SGInputLoader is a module in SGComps that will do a typeless StoreGate read
# of data on disk, to preload it in the Whiteboard for other Alorithms to use.
# It uses the same syntax as Algorithmic dependency declarations.
from AthenaCommon import CfgMgr
topSeq += CfgMgr.SGInputLoader(OutputLevel = INFO, ShowEventDump=False)
topSeq.SGInputLoader.Load = [('McEventCollection','StoreGateSvc+GEN_EVENT')]

# Add the beam effects algorithm
from AthenaCommon.CfgGetter import getAlgorithm
topSeq += getAlgorithm("BeamEffectsAlg", tryDefaultConfigurable=True)

# Add the (python) G4 simulation service.
# This will kickstart a lot of simulation setup.
from G4AtlasApps.PyG4Atlas import PyG4AtlasSvc
svcMgr += PyG4AtlasSvc()

# Explicitly specify the data-flow dependencies of G4AtlasAlg and StreamHITS.
# This is done like this because currently our VarHandles do not live in the
# algorithm but rather in Geant4 components.
# TODO: make this declaration more automatic
topSeq.G4AtlasAlg.ExtraInputs =  [('McEventCollection','StoreGateSvc+BeamTruthEvent')]
topSeq.G4AtlasAlg.ExtraOutputs = [('SiHitCollection','StoreGateSvc+SCT_Hits')]
topSeq.StreamHITS.ExtraInputs += topSeq.G4AtlasAlg.ExtraOutputs

# Increase verbosity of the output stream
#topSeq.StreamHITS.OutputLevel = DEBUG

# Disable alg filtering - doesn't work in multi-threading
topSeq.StreamHITS.AcceptAlgs = []

# Override algorithm cloning settings
algCardinality = jp.ConcurrencyFlags.NumThreads()
if (algCardinality != 1):
    for alg in topSeq:
        name = alg.name()
        if name == 'StreamHITS':
            alg.Cardinality = 1
        else:
            alg.Cardinality = algCardinality

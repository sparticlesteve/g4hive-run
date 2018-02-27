from AthenaCommon.AppMgr import theApp
from IntelProfiling.IntelProfilingConf import VTuneProfilerSvc
svcMgr += VTuneProfilerSvc('VTuneProfilerSvc', OutputLevel=DEBUG)
theApp.CreateSvc += [ 'VTuneProfilerSvc' ]

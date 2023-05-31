import numpy as np


from .RangeCompression import RangeCompression
from .DopplerProcessing import DopplerProcessing
from .CFAR import CFAR_1D
from Plots import PlotCFAR


def SignalProcesingAlgorithem(data,argArtifacts,range_setting):
    
    range_cube =  RangeCompression(data,axis=1)
   
    linear= DopplerProcessing(range_cube, axis=0,isClutterRemoval=True)
    
    linear[argArtifacts] = 1e-10
    mask = np.arange(linear.shape[0]) < 120
    formated = linear[mask]
    detections_map,detections_cord = CFAR_1D(np.abs(formated).copy(), 4, 8, 0.01,range_setting)
    #PlotCFAR(detections_map)
    return detections_cord

def Artifacts(data):
   
    range_cube =  RangeCompression(data,axis=1)
   
    linear = DopplerProcessing(range_cube, axis=0,isClutterRemoval=True,removeArtifacts=False)
    
    old = np.abs(linear).copy()
   
    argArtifacts = np.nonzero(old >4*np.mean(old[:,50]))
   
    return argArtifacts


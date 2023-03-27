import numpy as np


from .RangeCompression import RangeCompression
from .DopplerProcessing import DopplerProcessing
from .CFAR import CFAR_1D

def SignalProcesingAlgorithem(data,argArtifacts):
    range_cube =  RangeCompression(data,axis=1)
    linear, mag = DopplerProcessing(range_cube, axis=0,isClutterRemoval=True)
    linear[argArtifacts] = 1e-10
    detections_map,P_detections,detections, detections_cord,det_tuples = CFAR_1D(np.abs(linear).copy(), 4, 8, 0.01)
    return detections_cord , detections_map

def Artifacts(data):
    range_cube =  RangeCompression(data,axis=1)
    linear, mag = DopplerProcessing(range_cube, axis=0,isClutterRemoval=True,removeArtifacts=False)
    old = np.abs(linear).copy()
    argArtifacts = np.nonzero(old >4*np.mean(old[:,50]))
    return argArtifacts


from TrackingV2.KalmanFilterTracker import KalmanFilterTracker,Track_Tree
from TrackingV2.TentativTrack import TentativTrack
from TrackingV2.MHT import TOMHT
from Plots import PlotCFAR,PlotTracks
import matplotlib.pyplot as plt
import numpy as np
import firebase
import time
from datetime import datetime  
import logging


def TrackingProcess(exit_event,SP_data_queue,tracking_queue,range_setting=200):
    # Path: TrackingProcess.py
    # Function: TrackingProcess
    # Input: signal
    # Output: signal
    # Description: This function is used to process the signal
    logging.info("Started tracking")
    # fig = plt.figure(figsize=(10,10))
    
        
    
    # plt.xticks(np.linspace(0,256,9),labels=np.round(np.linspace(0,255*0.785277,9)),size =10)
    # plt.yticks(np.linspace(0,256,7),labels=np.round(np.linspace(-0.127552440715*127,0.127552440715*127,7),2),size =10)
    
    # #plt.xticks(np.linspace(0,256,9),size =10)
    # #plt.yticks(np.linspace(0,256,7),size =10)
    # plt.ylabel("Velocity [knots]",fontdict = {'fontsize' : 20})
    # plt.xlabel("Range [m]",fontdict = {'fontsize' : 20})
    # plt.title("Tracking",fontdict = {'fontsize' : 30})
    # plt.grid(False)
    # plt.legend()
    
    
    MHT = TOMHT()
    i = 0
    save_coords = []
    tentativ_tracks = []
    while not exit_event.is_set():
            i+=1
            data = SP_data_queue.get()
            if data is not None:
                MHT.Firm(data)
                unused_det = MHT.Perliminary(unused_det)
                perliminary_tracks = MHT.get_perliminery()
                firm_tracks = MHT.get_firm()
                new_preliminary_tracks,tentativ_tracks = TentativTrack(tentativ_tracks, unused_det)
                for new_track_i in new_preliminary_tracks:
                    MHT.new_track(new_track_i)
                if(len(firm_tracks)>0):
                    
                                  
                    firebase.ref.child(f'tracks/{time.time_ns()}').set(firm_tracks)
                    
        
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
from Utils import check_internet_connection


def TrackingProcess(exit_event,SP_data_queue,tracking_queue,range_setting):
    
    logging.info("Started tracking")
   
    
    
    MHT = TOMHT(range_setting)
    i = 0
    save_coords = []
    tentativ_tracks = []
    time_arr = []
    while not exit_event.is_set():
            i+=1
            
            data = SP_data_queue.get()
            drop_count = data[0]
            # if data is None:
            #     data =  np.empty((0,2))
            if data is not None:
                start = time.time()
                
                unused_det = MHT.Firm(data[1],drop_count)
                unused_det = MHT.Perliminary(unused_det,drop_count)
                perliminary_tracks = MHT.get_perliminery()
                firm_tracks = MHT.get_firm()
                new_preliminary_tracks,tentativ_tracks = TentativTrack(tentativ_tracks, unused_det,drop_count)
                for new_track_i in new_preliminary_tracks:
                    MHT.new_track(new_track_i)
                if(len(firm_tracks)>0):

                
                   
                            
                            firebase.ref.child(f'tracks/{time.time_ns()}').set(firm_tracks)
                    
                end = time.time()
                time_arr.append(end-start)    
                
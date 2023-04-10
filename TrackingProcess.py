from Tracking.TOMHT import TOMHT
from Tracking.Initiator import Initiator
from Plots import PlotCFAR,PlotTracks
import matplotlib.pyplot as plt
import numpy as np
import firebase
import time
from datetime import datetime  


def TrackingProcess(SP_data_queue,tracking_queue):
    # Path: TrackingProcess.py
    # Function: TrackingProcess
    # Input: signal
    # Output: signal
    # Description: This function is used to process the signal
    print("Started tracking")
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
    
    initiat = Initiator(3,5)
    tracker = TOMHT()
    i = 0
    save_coords = []
    while True:
            i+=1
            data = SP_data_queue.get()
            if data is not None:
                cords, unused_measurments,tracks = tracker.main(data)
                detections,tar = initiat.main(unused_measurments)
                if(len(detections)>0):
                    tracker.new_track(tar)
                if(len(tracks)>0):
                    print("test",tracks)
                    current_time = time.localtime()                
                    firebase.ref.child(f'tracks/{time.time_ns()}').set(tracks)
                    save_coords += cords
                    #print(cords)
                    #print(track for track in tracks)
                    #plt.plot([det[0] for det in cords], [det[1] for det in cords], 'ro',label="Tracking")
                    
                    #PlotTracks(save_coords)
            # if(i==95):
            #     plt.savefig(f"plots/tracks/Tracks_all.png")
            #     plt.close()

            #tracking_queue.put(tracks)
   
        
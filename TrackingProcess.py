from Tracking.TOMHT import TOMHT
from Tracking.Initiator import Initiator

def TrackingProcess(SP_data_queue,tracking_queue):
    # Path: TrackingProcess.py
    # Function: TrackingProcess
    # Input: signal
    # Output: signal
    # Description: This function is used to process the signal
    initiat = Initiator(3,5)
    tracker = TOMHT()
    while True:
        data = SP_data_queue.get()
        if tracker is not None:
            tracks, unused_measurments = tracker.main(data)
            detections,tar = initiat.main(unused_measurments)
            if(len(detections)>0):
                tracker.new_track(tar)
            print(tracks)
        tracking_queue.put(tracks)
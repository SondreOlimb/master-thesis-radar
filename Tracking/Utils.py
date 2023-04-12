from collections import deque
import numpy as np
def TrackMaintinance(tracks, max_age=10, min_hits=3,del_tresh=0.3):
    detections = []
    delete_tracks = []
    for track in tracks:
        
        if(sum(tracks[track].track_history)/len(tracks[track].track_history) < del_tresh and len(tracks[track].track_history) > 3 or sum(tracks[track].track_history) == 0 ):
            delete_tracks.append(tracks[track].track_id)
        
        elif sum(tracks[track].track_history)>min_hits :
            detections.append([tracks[track].x,tracks[track].vx])
    for track in delete_tracks:
        del tracks[track]
    return tracks,detections    




class Track:
    """Class representing a track"""
    
    def __init__(self, track_id, x,  vx, kalman_filter,track_age, track_history,track_length=5 ):
        self.track_id = track_id
        self.track_age = track_age
        self.x = kalman_filter.x[0]
        self.vx = kalman_filter.x[1]
        self.kalman_filter = kalman_filter
        self.track_history = track_history
        self.track_history_range = deque([kalman_filter.x_iso[0]])
        self.track_length = track_length

        
        
   
    
    def update(self, x, vx,hist=1):
        """Updates the state of the track with a new observation."""
        #print("update",self.kalman_filter.x_iso)
        self.kalman_filter.update(np.array([x,vx]))
        self.vx = self.kalman_filter.x[1]
        self.x = self.kalman_filter.x[0]
        
        self.track_age += 1
        self.track_history.append(hist)
        self.track_history_range.append(self.kalman_filter.x_iso[0])
        if(len(self.track_history)>self.track_length):
            
            self.track_history.popleft()
        if len(self.track_history_range)>self.track_length:
            self.track_history_range.popleft()
    def no_update(self):
        """Updates the state of the track with a new observation."""
        self.track_age += 1
        self.track_history.append(0)
        #self.track_history_range.append(self.kalman_filter.x_iso[0])
        if(len(self.track_history)>self.track_length):
            self.track_history.popleft()
        if len(self.track_history_range)>self.track_length:
            self.track_history_range.popleft()
    def nis(self,z):
        return self.kalman_filter.nis(z)

    def predict(self):
        """Propagates the state distribution to the current time."""
        
        self.kalman_filter.predict()
        self.vx = self.kalman_filter.x[1]
        self.x = self.kalman_filter.x[0]
        
        self.track_history.append(0)
        #self.track_history_range.append(self.kalman_filter.x_iso[0])
        if(len(self.track_history)>self.track_length):
            self.track_history.popleft()
        # if len(self.track_history_range)>self.track_length:
        #     self.track_history_range.popleft()
    def get_state(self):
        """Returns the current state of the track."""
        
        return self.kalman_filter.x
    def get_prediction(self):
        """Returns the current state of the track."""
        return self.kalman_filter.get_prediction()

    def __str__(self):
        return f"ID:{self.track_id}, Range:{round(self.kalman_filter.x[0]*0.785277,2)}, V:{round((128-self.kalman_filter.x[1])*-0.12755,2)}, History:{self.track_history}"
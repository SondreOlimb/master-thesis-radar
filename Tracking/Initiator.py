from collections import deque
import numpy as np
from .Utils import *
from .KF import KalmanFilter
from scipy.linalg import inv

from scipy.spatial import distance
from scipy.optimize import linear_sum_assignment
P_init = np.diag([10, 10])  # initial covariance matrix

Q = np.diag([15, 0])  # process noise covariance
#R = np.diag([1,1])  # measurement noise covariance
R = np.array([[  4.11455458 ,-16.52043271],
 [-16.52043271 , 66.33152914]])
dt = 50*1e-3
class Initiator:
    """Initiates new tracks."""

    def __init__(self,M,N ):
        self.tracks = []
        self.potential_targets = np.empty((0,2))
        self.M = M
        self.N = N
        self.id = 0
        self.treshold = 5

    def initiate(self, z):
        """Initiates a new track."""
        
        self.potential_targets =np.append( self.potential_targets,z,axis=0)
        
       
    def preliminary_track(self, z):
        """Initiates a new track."""
        if( len(self.tracks) == 0 ):
            print("no tracks")
            return z
       
        if z is None:
            return None
        NIS_mat = np.empty((len(self.tracks),len(z)))
        
        for t,track in enumerate( self.tracks):
            
            
            for m,mesurement in enumerate(z):
                assert mesurement[0] < 120, f"The velocity is posisitve: {mesurement}" 
                
                
                NIS = track.kalman_filter.nis(np.array([mesurement[1],mesurement[0]])) #(np.array([mesurement[1],mesurement[0]]) - H@track.kalman_filter.x_iso).T @ inv(S) @ (np.array([mesurement[1],mesurement[0]]) - H@track.kalman_filter.x_iso )
                
                if NIS <= self.treshold:
                    assert mesurement[0] < 120, f"The velocity is posisitve: {mesurement}" 
                    assert abs(mesurement[1]*0.785277 - track.kalman_filter.x_iso[0]) < 10, f"Range is too large: {mesurement[1]*0.785277 , track.kalman_filter.x_iso[0],track.track_history_range, NIS}"
                    NIS_mat[t,m] = NIS
                    
                else:
                    
                    NIS_mat[t,m] = 10000

        nis_c = NIS_mat.copy()
        unused_meas = z[np.all(NIS_mat ==10000, axis=0)]
        z = z[~np.all(NIS_mat ==10000, axis=0)]
        
        NIS_mat = NIS_mat[:,~np.all(NIS_mat==10000, axis=0)]
        unused_tracks = np.all(NIS_mat==10000, axis=1)
        
        row_ind, col_ind = linear_sum_assignment(NIS_mat)
        used_idx = []
       
        for r,c in zip(row_ind, col_ind):
           
            if (not unused_tracks[r]):
               
                assert abs( self.tracks[r].kalman_filter.x_iso[0]-z[c][1]*0.785277) < 10, f"Range is too large: {z[c][1] , track.kalman_filter.x_iso[0]}"\
                    
                self.tracks[r].update(z[c][1],z[c][0],1)
                used_idx.append(self.tracks[r].track_id)
            
            
            
        for track in self.tracks:
            if track.track_id not in used_idx:
                
                track.no_update()
                
        
        
        return unused_meas
                    
                    

    def process_initiator(self,measurments,max_distance = 3):
        
        if( self.potential_targets.size == 0 ):return measurments
        if(measurments.size == 0):
            self.potential_targets = np.empty((0,2))
            return None
        
        euclidian_distance = distance.cdist(self.potential_targets, measurments, 'euclidean')
        euclidian_distance[euclidian_distance>max_distance] = 100000
        
        unused_meas = measurments[np.all(euclidian_distance==100000, axis=0)]
       
        euclidian_distance = euclidian_distance[:,~np.all(euclidian_distance ==100000, axis=0)]
        
        try:
       
            _, col_ind = linear_sum_assignment(euclidian_distance)
        except Exception as e:
            print("error",euclidian_distance)
           
            print(e)
            
       
        for i in col_ind:
            assert measurments[i,0] < 130, f"The velocity is posisitve: {measurments[i,0]}" 
            kf =KalmanFilter(dt, np.array([measurments[i,1], measurments[i,0]]),P_init,Q,R)
            track = Track(self.id+1, measurments[i,1], measurments[i,0],kf ,track_age = 0,track_history=deque([1]),track_length=5)
            self.tracks.append(track)
            
            
            
            self.id += 1
        
        self.potential_targets = np.empty((0,2))
       
        return unused_meas
    def trackMaintinance(self,max_age=10, N=3,M=5):
        
        confirmed_tracks = []
        delete_tracks = []
        potential_tracks = []
        retrun_tracks = []
        for track in self.tracks:
            delta_r_theoretical = track.kalman_filter.x_iso[1]*50*1e-3
            delta_r_real = max(track.track_history_range)-min(track.track_history_range)
            assert delta_r_real < 10, f"delta_r_real is too big: {track} \n {delta_r_real} \n {track.track_history_range}"
            if(sum(track.track_history) < N and len(track.track_history) >= M ):
                delete_tracks.append(track)
                print("deleted",track)
              
            elif sum(track.track_history)>=N: #q and delta_r_real >=abs(delta_r_theoretical)*len(track.track_history) *0.7:
                print("\n",delta_r_real ,abs(delta_r_theoretical*len(track.track_history) *0.9))
                print(track.track_history_range)
                print("CONFIRMED",track)
                #track.track_history = deque([1,1,1,1,1])
                confirmed_tracks.append([track.kalman_filter.x[0],track.kalman_filter.x[1]])
                #potential_tracks.append(track)
                retrun_tracks.append(track)
                #input("Press Enter to continue...")
                #print([track.kalman_filter.x[0],track.kalman_filter.x[1]])
                #print(track.kalman_filter)
                #print("confirmed",track)
            else:
                potential_tracks.append(track)
                #print("POTENTIAL",track)
        self.tracks = potential_tracks
        #print("\n")
        return confirmed_tracks,retrun_tracks
    

    def main(self, measurments):
        """Initiates new tracks and manages track list."""
        #self.preliminary_track(measurments)
        #print("measurments",measurments.shape)
        #print("\n", "##TRACKS##")
       # [print(tr) for tr in self.tracks]
        #print("\n")
        meas = self.preliminary_track(measurments)
        meas = self.process_initiator(meas)
        if(meas is not None):
            self.initiate(meas)
        

        return self.trackMaintinance()


        
           
           
            

       

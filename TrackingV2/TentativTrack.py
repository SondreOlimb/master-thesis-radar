import numpy as np
from scipy.spatial import distance
from scipy.optimize import linear_sum_assignment



def TentativTrack(tracks,detections,dt =50*10**(-3)):
    """_summary_

    Args:
        tracks (nd.array): an nd array of tentativ tracks [[velocity,range],....]
        detections (_type_): An nd.array of new detections [[velocity,range],....]
    """
    if(len(tracks)==0):
        return np.array([]),detections
    if(detections.shape[1] == 0):
        return np.array([]),np.array([])
    
    try:   
        euclidian_distance = distance.cdist(tracks,detections,'euclidean')
    except Exception as e:
            print("Tracks: ", tracks)
            print("detections",detections.shape)
            print(e)
            exit()
    gate = tracks[:,1]*dt*1.5
    gate =np.array([gate]*detections.shape[0]).T
    range_resolution = 0.7852
    velocity_resolution = 0.2362
    
    euclidian_distance[euclidian_distance>gate] = 10000
    
    tracks = tracks[:, np.newaxis, :]  # add a new axis to the tracks array@
    
    euclidian_distance[detections[:,1] > tracks[:,:,1]] = 10000 #range cant be larger than the track range
    
        #Velovity cant deviate significantly from the track velocity
    euclidian_distance[detections[:,0] < tracks[:,:,0]-velocity_resolution*1] = 10000
    euclidian_distance[detections[:,0] > tracks[:,:,0]+velocity_resolution*1] = 10000
    euclidian_distance[detections[:,1] < tracks[:,:,1]-range_resolution*1] = 10000
    euclidian_distance[detections[:,1] > tracks[:,:,1]+range_resolution*1] = 10000


    
    unused_detections = detections[np.all(euclidian_distance==10000, axis=0)]
    
    euclidian_distance = euclidian_distance[:,~np.all(euclidian_distance ==10000, axis=0)]
    
    try:
       
        _, col_ind = linear_sum_assignment(euclidian_distance)
    except Exception as e:
            print("error",euclidian_distance)
            # print(self.potential_targets, measurments)
            print(e)
    if len(col_ind) >0:
        
        print("Perliminary Track: ", detections[col_ind])
   
    return detections[col_ind], unused_detections

        

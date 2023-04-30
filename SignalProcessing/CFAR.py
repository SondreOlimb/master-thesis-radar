from scipy.ndimage import convolve1d
import numpy as np
from sklearn.cluster import DBSCAN

def P_avg(P,N):
    return P
def alpha(N,P_FA):
    return(P_FA**(-1/N)-1)

def estimated_teshold(alpha,P):
    return alpha*np.abs(P)


def CFAR_1D(data, guard_cells, training_cells, PFA,range_setting = 0.785277,cluster =True):
    
    
    window_size = guard_cells + training_cells
    
    window_area = (2*window_size+1)**2
    training_area = training_cells*2
    a = alpha(training_area, PFA)

    kernel = np.ones((1 + (2 * guard_cells) + (2 * training_cells)), dtype=data.dtype)
    kernel[training_cells:training_cells + (2 * guard_cells) + 1] = 0
    
    res = convolve1d(data, kernel, mode='wrap')
    
    
    ret = (np.abs(data)>estimated_teshold(a,res))
    
    detections = np.argwhere(ret==True)
    #Transform cords to ran #print(detections)
    

    detections = detections[detections[:,0] < 120,:]#delete all irelevant detections
    
    

    detections[:,1] = detections[:,1]*range_setting
    detections[:,0] = (128-detections[:,0])*-0.065614
    detections = detections.astype(np.float16)
    if(detections.shape[0] == 0):
        return ret ,detections
    if(cluster):
        dbscan = DBSCAN(eps=0.5, min_samples=1)
        dbscan.fit(detections)
        labels = dbscan.labels_
        
        unique_labels = set(labels)
        centers = []
        for label in unique_labels:
            if label == -1:
                # Skip outliers
                continue
            cluster_points = detections[labels == label]
            center = np.mean(cluster_points, axis=0)
            centers.append(center)
        detections = np.array(centers)

            
    return ret,detections
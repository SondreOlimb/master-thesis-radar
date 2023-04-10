import copy
import numpy as np
from scipy.stats import multivariate_normal, poisson

import networkx as nx

# Define the state transition model
F = np.array([[1, 1],
              [0, 1]])

# Define the measurement model
H = np.array([[1, 0],
              [0, 1]])

# Define the covariance matrices
Q = np.diag([0.1, 0.01])
R = np.diag([0.1, 0.1])

# Define the clutter intensity
lambda_c = 1e-5

# Define the threshold for creating new tracks
threshold = 0.5

# Define a class for a track
class Track_Tree:
    def __init__(self, new_track):
        print("track initiated")
        self.track_three =nx.DiGraph()
        self.track_three.add_nodes_from([(0,{"track":new_track,"score":0,"number":0,"label":"root"})])
        self.node_number = 0
        
        self.hits = 1
    
    
    def predict(self):
        leaf_nodes = self.get_leaf_nodes()
        for node in leaf_nodes:
            self.track_three.nodes[node]['track'].predict()
    
    def get_prediction(self):
        return self.x, self.P
    
    def add_node(self,parent_node ,track,score,label):
        self.node_number +=1
        data = {'track':track,"score":score,"number":self.node_number,"label":label}
        
        self.track_three.add_nodes_from([(self.node_number,data)])
        
        self.track_three.add_edge(parent_node,self.node_number)
       
        
    
    def get_state(self):
        return self.x
    def get_leaf_nodes(self):
        leaf_nodes = set()
        all_nodes = set(self.track_three.nodes())

        for node in all_nodes:
            descendants = nx.descendants(self.track_three, node)
            if not descendants:
                leaf_nodes.add(node)
        return leaf_nodes
    def __str__(self):
        return str(self.track_three.nodes.data())
     
# Define a class for the tracker
class TOMHT:
    def __init__(self):
        self.tracks = []
        self.treshold = 0.5
    
    
    
    def get_tracks(self):
        tracks = []
        for track in self.tracks:
            tracks.append(track.get_state())
        return tracks
    
    def gate(self, z,track):
        
        return track.nis(np.array([z[1],z[0]])) < self.treshold
    
    def get_score(self, track,old_score,z= None ,range =200, ilumination_angle=30):
        lambda_clutter  = 4e-6 # expected nomber of clutter or FA per scan
        lambda_new = 1e-5 # expected nomber of new targets per scan
        lambda_ex = 1e-5 # expected nomber of existing targets per scan
        P_D = 0.9 # probability of detection
        #area = (np.pi * np.power(range, 2))*ilumination_angle/360
        #gClutter = lambda_phi * area

        
        S = H @ track.kalman_filter.P @ H.T + R
        if z is None:
            z = track.get_prediction()
        
        score = (0.5 * track.nis(z) + np.log((lambda_ex * np.sqrt(np.linalg.det(2 * np.pi * S))) / P_D))

        return old_score+score

    def new_track(self, tracks):
        for track in tracks:
            self.tracks.append(Track_Tree(track))
    def pruning(self,track,best_node,N=2):
        neighbors = nx.descendants_at_distance(track, best_node, distance=N)
        neighbors.add(best_node)
        
        track.remove_nodes_from([node for node in track.nodes() if node not in neighbors])
       
    def track_maintainance(self,score,track,treshold=-6):
        """
        If the score is below the treshold or the track is not moving, the track is removed

        Args:
            score (_type_): _description_
            track (_type_): _description_
            treshold (int, optional): _description_. Defaults to -6.

        Returns:
            _type_: _description_
        """
        delta_r_theoretical = track.kalman_filter.x_iso[1]*50*1e-3/1.94384 #kovert to m/s
        delta_r_real = max(track.track_history_range)-min(track.track_history_range)
        #print("Track maintainance")
        #print(track.track_history_range)
        #print(delta_r_real ,abs(delta_r_theoretical)*len(track.track_history) *0.9)
        if delta_r_real < abs(delta_r_theoretical)*len(track.track_history) *0.6:
            # print("REMOVED")
            # print("Removed",track,score)
            # print("Track maintainance")
            # print(track.track_history_range)
            # print(delta_r_real ,abs(delta_r_theoretical)*len(track.track_history) *0.9)
            #input("Press Enter to continue...")
            return False
        # if score > treshold:
        #     print("Removed",track,score)
        #     print("Track maintainance")
        #     print(track.track_history_range)
        #     print(delta_r_real ,abs(delta_r_theoretical)*len(track.track_history) *0.9)
        #     #input("Press Enter to continue...")
        return score < treshold 



    def main(self,measurements):
        #print("main")
        tracking_cords = []
        used_measurements = []
        tracks_return = []
        if len(self.tracks) == 0:
            return [],measurements ,self.tracks
        for track in self.tracks:
            
            #create zero hypothesis
            
            leaf_nodes = track.get_leaf_nodes()
           
            for node in leaf_nodes:
                #print(node,track.track_three.nodes[node]["track"])
                
                score = self.get_score(track.track_three.nodes[node]["track"],track.track_three.nodes[node]["score"])
                track_pred = copy.deepcopy(track.track_three.nodes[node]["track"])
                track_pred.predict()
                track.add_node(node,track_pred,score,"zero")
               
                #NEED TO UPDATE THE AGE
                
                gated_meas =[] #[meas used_measurements.append(idx) for idx ,meas in enumerate(measurements) if self.gate(meas,track.track_three.nodes[node]["track"])  ]
                for idx ,meas in enumerate(measurements):
                    if self.gate(meas,track.track_three.nodes[node]["track"]):
                        #print("gated",f"Range:{meas[1]*0.785277}, V:{(128-meas[0])*-0.12755}")
                        gated_meas.append(meas)
                        used_measurements.append(idx)
                #print("gated",gated_meas)
                for meas in gated_meas:
                    #print("gated",f"Range:{meas[1]*0.785277}, V:{(128-meas[0])*-0.12755}")
                    score = self.get_score(track.track_three.nodes[node]["track"],track.track_three.nodes[node]["score"],np.array([meas[1],meas[0]]))
                    track_update = copy.deepcopy(track.track_three.nodes[node]["track"])

                    track_update.update(meas[1],meas[0])
                    track.add_node(node,track_update,score,"update")
                
            # print("#################")
            # for node in track.track_three.nodes:
                
            #     print(node,track.track_three.nodes[node]["track"],track.track_three.nodes[node]["score"])
            leaf_nodes = track.get_leaf_nodes()
            
            score = 0
            best_node = None
           
            
            
            for node in leaf_nodes:
                if track.track_three.nodes[node]["label"] == "zero":
                    best_node = node #if there is only zero hypothesis
                if track.track_three.nodes[node]["score"] < score and track.track_three.nodes[node]["label"] == "update":
                        
                    score = track.track_three.nodes[node]["score"]
                    best_node = node
            
            #print(track.track_three.nodes[best_node]["track"],"Score",track.track_three.nodes[node]["score"],track.track_three.nodes[best_node]["label"])
            #print("MHT",track.track_three.nodes[best_node]["track"])
            
           
            if self.track_maintainance(track.track_three.nodes[best_node]["score"], track.track_three.nodes[best_node]["track"]):
                track.track_three.nodes[best_node]["score"] =0
                tracking_cords.append(track.track_three.nodes[best_node]["track"].get_state() )
                tracks_return.append(track.track_three.nodes[best_node]["track"])
                print(track.track_three.nodes[best_node]["track"])
                self.pruning(track.track_three,best_node)
            else:
                self.tracks.remove(track)
               

        
        
        unused = np.delete(measurements, used_measurements, axis=0)
        
        #input("Press Enter to continue...")
        
        return tracking_cords, unused, tracks_return
                    
from scipy.optimize import linear_sum_assignment
import numpy as np
from .KalmanFilterTracker import Track_Tree
import networkx as nx
import matplotlib.pyplot as plt
from scipy.optimize import linprog
import logging
class TOMHT:
    def __init__(self):
        self.tracks = []
        self.firm_tracks = []
        self.treshold = 5
        self.frame = 0
        self.track_id = 0
    
    
    
   
    
    def Perliminary(self, detections):
        
        GH = []
        selected_nodes = []
       
        if len(self.tracks) == 0:
            return np.array(detections)
        unused_detections = detections
        for tr,track in enumerate(self.tracks):
           

            D2TA,selected = track.get_D2TA(detections,self.frame)
            
            if(len(D2TA)>0):
                GH.append(D2TA)
                selected_nodes.append(selected)
        
            
        
        if(len(GH) != 0):
            GH = np.array(GH)
        
            unused_detections = detections[np.all(GH==10000, axis=0)]
           
            row_ind, col_ind = linear_sum_assignment(GH)
            
            for r,c in zip(row_ind, col_ind):
            #for alle som ikke blir satt her må vi sette til nul hypotese   
                dec = np.array(list(nx.descendants(self.tracks[r].track_three,selected_nodes[r])))
                if GH[r][c] != 10000:
                        
                        dec_sel = dec[np.char.find(dec.astype(str), str(self.frame) +"_"+ str(c) ) != -1]
                        self.tracks[r].selected_node = dec_sel[0]
                        self.tracks[r].x = self.tracks[r].track_three.nodes[self.tracks[r].selected_node]['track'].x_iso
             
                
        
        self.frame +=1
        self.track_maintinance()
        return unused_detections           
    def Firm(self, detections):
        self.frame +=1
        GH = []
        if len(self.firm_tracks) == 0:
            
                return np.array(detections)
        unused_detections = detections.copy()
        used_detections = np.empty((0,2),dtype="float16")

        A_ub = np.array([]) #Hypotese matrix A_ub in documentation
        hyp_ids_lp = np.array([])#
        A_eq = np.array([]) #Hypotese matrix A_eq in documentation
        c= np.array([]) #Hypotese score c in documentation
        hyp_nodes_lp = np.array([])
        tracks_for_Consideration = [] 
        
        for tr,track in enumerate(self.firm_tracks):
            
            det = track.Create_Firm_D2TA(detections,self.frame)
            if(len(det)>0):
                used_detections =np.concatenate((used_detections,det),axis=0)
                
            
            hypot,nodes,ids,score = track.create_path_matrix()
            
            hyp_nodes = nodes
            hyp_nodes_score = score
            if(len(used_detections)!=0):
                    
                    mask = ~np.isin(detections, used_detections).all(axis=1)
                    diff = detections[mask]
                    
                    
                    unused_detections = diff.reshape((-1, 2))
            else:
                    unused_detections = detections
            
            if(len(ids) == 0 and len(self.firm_tracks) > 1 ):
                track.selected_node = hyp_nodes[np.argmin(hyp_nodes_score)]
                track.x = track.track_three.nodes[track.selected_node]['track'].x_iso
            else:
                tracks_for_Consideration.append(tr)
                hyp_nodes_lp = np.concatenate((hyp_nodes_lp,nodes),axis=0)

                A_eq = self.bool_matrix(A_eq,len(hyp_nodes))
                c = np.concatenate((c,score),axis=0)
                hyp_ids_lp,A_ub= self.Create_hyp(A_ub,hypot,hyp_ids_lp,ids,)
                
            
            
            if(len(self.firm_tracks) == 1):
                
                track.selected_node = hyp_nodes[np.argmin(hyp_nodes_score)]
               
                track.x = track.track_three.nodes[track.selected_node]['track'].x_iso
                track.Pruning(track.selected_node)
                
                
                track.Pruning(track.selected_node)
                
                
                
            

                
                
            
        if(len(self.firm_tracks)>1 and len(tracks_for_Consideration)>1):
            b_ub = np.ones(len(hyp_ids_lp))
            b_eq = np.ones(len(tracks_for_Consideration))
            res =np.round( linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=(0, 1), method='simplex',).x)
            selected_hyp = hyp_nodes_lp[res == 1]
            track_ids = np.argwhere(A_eq[:,:] ==1)
            track_ids = track_ids[res == 1]
         
            for n,t_ids in enumerate(track_ids):
                    
               
                try:
                    self.firm_tracks[tracks_for_Consideration[t_ids[0]]].selected_node = selected_hyp[n]
                    self.firm_tracks[tracks_for_Consideration[t_ids[0]]].x = self.firm_tracks[tracks_for_Consideration[t_ids[0]]].track_three.nodes[self.firm_tracks[tracks_for_Consideration[t_ids[0]]].selected_node]['track'].x_iso
                    self.firm_tracks[tracks_for_Consideration[t_ids[0]]].Pruning(self.firm_tracks[tracks_for_Consideration[t_ids[0]]].selected_node)
                except Exception as e:
                    logging.critical(f"Error in firm track: {e}")
                    self.firm_tracks = []
                    return np.array(detections)
                    
                    
                    

            
            
        elif(tracks_for_Consideration == 1):
            self.firm_tracks[tracks_for_Consideration[0]].selected_node = hyp_nodes[np.argmin(hyp_nodes_score)]
            self.firm_tracks[tracks_for_Consideration[0]].x = track.track_three.nodes[track.selected_node]['track'].x_iso
            self.firm_tracks[tracks_for_Consideration[0]].Pruning(self.firm_tracks[tracks_for_Consideration[0]].selected_node)
        return unused_detections
        
            
           
        
        
        
    
    def get_perliminery(self):
        tracks = []
        for track in self.tracks:
            tracks.append(track.x)
        return tracks
    def get_firm(self):
        tracks = []
        for track in self.firm_tracks:
            if(sum(track.track_history)==0):
                self.firm_tracks.remove(track)
            
               
        for track in self.firm_tracks:
            
            if(np.isin(track.x,tracks).any()):
                self.firm_tracks.remove(track)
            
            else:
                track_dict = {"range": round(float(track.x[0]),2),"vel":round(float(track.x[1]),2), "id": track.id}
                logging.info(track)
                tracks.append(track_dict)
        return tracks
    
    def new_track(self,detection):
        
        self.track_id +=1 
        self.tracks.append(Track_Tree(self.track_id,detection))
    def track_maintinance(self):
        
        for track in self.tracks:
           
            track.Pruning(track.selected_node)
            if track.status == "perliminary":
                
                range_std = np.std(track.track_history_range)
                if sum(track.track_history) < 3 and len(track.track_history) == 5:
                    self.tracks.remove(track)
                    
                    
                   
                
                elif(range_std < 0.1 and len(track.track_history) == 5):
                    self.tracks.remove(track) 
                    
                elif sum(track.track_history) > 3 and range_std>0.1:
                   
                    
                    self.tracks.remove(track)
                    
                    track.status = "firm"
                    logging.info(f"Initiated tracks: STD:{range_std}, Track:{track}")
                   
                    
                    #input("firm")
                    
                    self.firm_tracks.append(track)
        for track in self.firm_tracks:
                range_std = np.std(track.track_history_range)
                
                if(range_std < 0.1 ):
                    logging.info(f"REMOVED Track becouse of STD: {track}")
                    self.firm_tracks.remove(track)
            
        
                    
    
    def Create_hyp(self,m1,m2,id1,id2):
        # concatenate the matrices and ID arrays
        
        if len(m1) == 0:
            # if len(m2) == 0:
            #     m2 = np.array([[0]])
            return id2,m2
        if(len(id2) == 0):
            
            m1 = np.concatenate((m1,np.zeros((1,m1.shape[0])) ),axis=1)
            
            return id1,m1
        ids = np.concatenate((id1, np.setdiff1d(id2, id1)), axis=0)
        ids_arg_sort = np.argsort(ids)
        ids = np.sort(ids)
        matrix_res = np.zeros((len(ids), m1.shape[1] + m2.shape[1]))
        matrix_res[:m1.shape[0], :m1.shape[1]] = m1
        #sort matrix rows after ids
        matrix_res = matrix_res[ids_arg_sort]
        # copy elements from matrix2 to matrix_res using boolean indexing
        ind_1 = np.searchsorted(ids, id2)
        ind_2 = np.searchsorted(id2,ids[ind_1])
        matrix_res[ind_1, m1.shape[1]:] = m2[ind_2]
        
        
        return ids, matrix_res


    def bool_matrix(self,matrix,n):
        if(matrix.shape[0] == 0):
            return np.ones((1,n), dtype=int)
        new = np.zeros((matrix.shape[0],n),dtype=int)
        matrix = np.vstack((matrix,np.zeros((1,matrix.shape[1]),dtype=int)))
        new = np.vstack( (new,np.ones((1,n), dtype=int)))
        new = np.concatenate((matrix,new),axis = 1)
        
        return new
   
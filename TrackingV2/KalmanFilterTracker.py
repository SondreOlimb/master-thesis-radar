import numpy as np
from scipy.linalg import inv
from collections import deque
import networkx as nx
import matplotlib.pyplot as plt


P_init = np.diag([10, 1])  # initial covariance matrix

Q = np.diag([0.1, 0])  # process noise covariance
R = np.diag([0.785277**2,0.0656168**2])  # measurement noise covariance
# R = np.array([[  4.11455458 ,-16.52043271],
#  [-16.52043271 , 66.33152914]])
dt = 50*1e-3

class KalmanFilterTracker(object):
    def __init__(self, x,range_setting, P_init =P_init, Q=Q, R=R, dt= dt):
        self.dt = dt  # time step
        self.range_setting = range_setting
        self.P = P_init  # initial covariance matrix
        self.Q = Q  # process noise covariance
        self.R = np.diag([range_setting**2,0.0656168**2])  # measurement noise covariance
        self.x_iso = np.array([0,0],dtype="float16")
        self.x_iso = x
        self.F = np.array([[1, self.dt], [0, 1]],dtype ="float16")  # state transition matrix
        
        self.track_history = deque([1])
        
       
        

    def predict(self,drop_count, u=None):
        self.F = np.array([[1, self.dt*drop_count], [0, 1]])
        # state transition matrix
        if u is not None:
            B = np.array([[(self.dt**2)/2], [self.dt]])  # control input matrix
            self.x_iso = self.F @ self.x_iso + B @ u
                      
        else:
            
           
            self.x_iso = self.F @ self.x_iso
            #print(self.x_iso)
          
        self.P = self.F @ self.P @ self.F.T + self.Q

    def get_prediction(self,drop_count):
        "this function onøy gets the prediction, but doese n"
        
        self.F = np.array([[1, self.dt*drop_count], [0, 1]])             
        pred = self.F @ self.x_iso
        
        return pred
            
   
    def update(self, z):
        
        
        z_iso = np.array((z[1],z[0]),dtype="float16")

        H = np.array([[1, 0], [0, 1]])  # observation matrix

        y = z_iso - H @ self.x_iso  # innovation
        
        self.S = H @ self.P @ H.T + self.R  # innovation covariance
        
        K = self.P @ H.T @ inv(self.S)  # Kalman gain
        
        #assert abs(self.x_iso[0] -z_iso[0]) < 10, f"RAnge delta to big: {self.x_iso}, {z}"
        try:
            self.x_iso = self.x_iso + K @ y  # updated state estimate
        except:
            
            exit()
        #assert abs(self.x_iso[0] -z[0]) < 10, f"RAnge delta to big: {self.x_iso}, {z}"
        
        self.P = (np.eye(2) - K @ H) @ self.P  # updated covariance matrix
        

    def Mahalanobis(self, z,drop_count):
       
        
        z_iso = np.array((z),dtype="float16")
        self.F = np.array([[1, self.dt*drop_count], [0, 1]])
        #self.predict()
        H = np.array([[1, 0], [0, 1]])
        P =  self.F @ self.P @ self.F.T + self.Q
        S = H @ P @ H.T + self.R
        K = self.P @ H.T @ np.linalg.inv(S)
        x_pred =self.F @ self.x_iso
        
            
        
        innovation = z_iso - H @ x_pred
       
        return innovation.T @ np.linalg.inv(S) @ innovation
    
    def NLLR(self,z,drop_count):
        self.F = np.array([[1, self.dt*drop_count], [0, 1]])
        lambda_ex = 1e-5 # expected nomber of existing targets per scan
        P_D = 0.9 # probability of detection
        z_iso = np.array((z),dtype="float16")
        H = np.array([[1, 0], [0, 1]])
        P =  self.F @ self.P @ self.F.T + self.Q
        S = H @ P @ H.T + self.R
        K = self.P @ H.T @ np.linalg.inv(S)
        x_pred =self.F @ self.x_iso
        innovation = z_iso - H @ x_pred
        return 0.5*(innovation.T @ np.linalg.inv(S) @ innovation) +np.log((lambda_ex * np.sqrt(np.linalg.det(2 * np.pi * S))) / P_D)
        
        

    def __str__(self):
        return f"Range: {round(self.x_iso[0],2)}, V: {round(self.x_iso[1],3)}"
    
    
class Track_Tree:
    def __init__(self,id, detection,range_setting,track_length=5):
        
        self.track_three =nx.DiGraph()
        self.range_setting = range_setting
        new_track =  KalmanFilterTracker(np.array([detection[1],detection[0]]),self.range_setting)
        #self.track_three.add_node(detection_id=0,track=new_track)
        self.track_three.add_nodes_from([(0,{"track":new_track,"score":0})])

        self.status = "perliminary"
        self.hits = 1
        self.id =id
        self.x = np.array([detection[1],detection[0]])
        self.track_history = deque([1])
        self.track_history_range = deque([detection[1]])
        self.track_history_vel = deque([detection[0]])
        self.track_length = track_length
        
        self.selected_node = "0"
        self.root = "0"
        
    
    def predict(self,drop_count):
        leaf_nodes = self.get_leaf_nodes()
        for node in leaf_nodes:
            self.track_three.nodes[node]['track'].predict(drop_count)
    def update_range_and_vel_history(self,r,v):
        self.track_history_range.append(r)
        if (len(self.track_history_range)>self.track_length):
            self.track_history_range.popleft()
        self.track_history_range.append(v)
        if (len(self.track_history_vel)>self.track_length):
            self.track_history_vel.popleft()

    def get_D2TA(self,detections,frame_number,drop_count):
        leaf_nodes = self.get_leaf_nodes()
        
        D2TA_cornfirmation  =0
        D2TA = []
        selected = self.selected_node
        count=0
        
        for n, node in enumerate(leaf_nodes):
            
            
            
            self.track_three.nodes[node]['track'].predict(drop_count)
            arg_D2TA, confirmed_D2TA_Score,D2TA_score = self.perliminary_D2TA(self.track_three.nodes[node]['track'],detections,drop_count)
               
            
            self.track_three.add_nodes_from([(str(n)+"_"+str(frame_number)+"_"+ "zero",self.track_three.nodes[node])])
            
            self.track_three.add_edge(node,str(n)+"_"+str(frame_number)+"_"+ "zero")
            self.selected_node = str(n)+"_"+str(frame_number)+"_"+ "zero"
            self.track_three.x = self.track_three.nodes[node]['track'].x_iso
            


            if len(arg_D2TA) > 0:
               
                D2TA_cornfirmation  =1
            for i, arg in enumerate(arg_D2TA):
                track_copy = self.track_three.nodes[node]['track']
            
                track_copy.update(detections[arg[0]])
                assert np.array_equal(self.track_three.nodes[node]['track'].x_iso,track_copy.x_iso ), f"Track not updated correctly"
                self.track_history_range.append(detections[arg[0]][1])
                self.track_history_vel.append(detections[arg[0]][0])
                self.track_three.add_nodes_from([(str(n)+"_"+str(frame_number)+"_"+ str(arg[0]),{"track":track_copy,"score":D2TA_score[arg[0]]})])
                self.track_three.add_edge(node,str(n)+"_"+str(frame_number)+"_"+ str(arg[0]))
                
                
            
            if node == self.selected_node:
                
                print(count)
                count+=1
                
                
                
                D2TA = D2TA_score
        self.track_history.append(D2TA_cornfirmation)
        
        
        
        
        
        if(len(self.track_history)>self.track_length):
            self.track_history.popleft()
        
        
        return D2TA,selected
    
    def Create_Firm_D2TA(self,detections, frame_number,drop_count):
        """
        This function is used to get the D2TA score for each detection in the frame which pases the gate. 
        nyew hypothesis are created from each D2TA

        Args:
            detections (_type_): _description_
            frame_number (_type_): _description_
        """
        D2TA_cornfirmation  =0
        used_detecions = []
        leaf_nodes = self.get_leaf_nodes()
        for n, node in enumerate(leaf_nodes):
            self.track_three.nodes[node]['track'].predict(drop_count)
            arg_D2TA, confirmed_D2TA_Score,D2TA_score = self.Firm_D2TA(self.track_three.nodes[node]['track'],detections,self.track_three.nodes[node]['score'],drop_count)
            
            self.track_three.add_nodes_from([(str(n)+"_"+str(frame_number)+"_"+ "zero",self.track_three.nodes[node])])
            
            self.track_three.add_edge(node,str(n)+"_"+str(frame_number)+"_"+ "zero")
            if len(arg_D2TA) > 0:
               
                D2TA_cornfirmation  =1
            for i, arg in enumerate(arg_D2TA):
                track_copy = self.track_three.nodes[node]['track']
                used_detecions.append(detections[arg[0]])
                track_copy.update(detections[arg[0]])
                assert np.array_equal(self.track_three.nodes[node]['track'].x_iso,track_copy.x_iso ), f"Track not updated correctly"
                self.track_three.add_nodes_from([(str(n)+"_"+str(frame_number)+"_"+ str(arg[0]),{"track":track_copy,"score":D2TA_score[arg[0]]})])
                self.track_three.add_edge(node,str(n)+"_"+str(frame_number)+"_"+ str(arg[0]))
        self.track_history.append(D2TA_cornfirmation)
        if(len(self.track_history)>self.track_length):
            self.track_history.popleft()
        return used_detecions
    def Firm_D2TA(self,track,detections,CNLLR,drop_count):
        
        D2TA =  np.empty(detections.shape[0])
       
        range_resolution = 0.7852
        velocity_resolution = 0.0656168
        
        gate_v_H = track.x_iso[1]-velocity_resolution*1.5 #track.x_iso[1]*(1+2/127)
        gate_v_L =track.x_iso[1]+velocity_resolution*1.5 #track.x_iso[1]*(1-2/127)
        gate_r_L = track.x_iso[0]-range_resolution*1.5 -np.abs(track.x_iso[1]*dt*(drop_count-1))
        gate_r_H = track.x_iso[0]+range_resolution*1.5 + np.abs(track.x_iso[1]*dt*(drop_count-1))
        for d,detection in enumerate(detections):
            if detection[1] > gate_r_H or detection[1]< gate_r_L:
                
                D2TA[d] = 10000
            elif detection[0] < gate_v_H or detection[0] > gate_v_L:
                
                D2TA[d] = 10000
            else:
                NLLR = track.NLLR(np.array([detection[1],detection[0]]),drop_count)
              
                D2TA[d] = CNLLR + NLLR
                
       
        return np.argwhere(D2TA != 10000),np.where(D2TA != 10000) ,D2TA


    def perliminary_D2TA(self,track,detections,drop_count,t =50*10**(-3),treshold=5):
        if(detections.shape[1] == 0):
            return np.array([]),np.array([]) ,np.array([])
        
        D2TA =  np.empty(detections.shape[0])
        
        range_resolution = 0.7852
        velocity_resolution = 0.0656168
        
        gate_v_H = track.x_iso[1]-velocity_resolution #track.x_iso[1]*(1+2/127)
        gate_v_L =track.x_iso[1]+velocity_resolution #track.x_iso[1]*(1-2/127)
        gate_r_L = track.x_iso[0]-range_resolution-np.abs(track.x_iso[1]*dt*(drop_count-1))
        gate_r_H = track.x_iso[0]+range_resolution +np.abs(track.x_iso[1]*dt*(drop_count-1))
        
        for d,detection in enumerate(detections):
            
            if detection[1] > gate_r_H or detection[1]< gate_r_L:
                
                D2TA[d] = 10000
            elif detection[0] < gate_v_H or detection[0] > gate_v_L:
                
                D2TA[d] = 10000
            else:
                Mahalanobis = track.Mahalanobis(np.array([detection[1],detection[0]]),drop_count)
                if Mahalanobis < treshold: 
                    
                    D2TA[d] = Mahalanobis
                else: D2TA[d] = 10000
       
        return np.argwhere(D2TA != 10000),np.where(D2TA != 10000) ,D2TA
        


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
        return f"Track:{self.id} {self.track_three.nodes[self.selected_node]['track']} \n Hits: {self.track_history}, Hist Range: {self.track_history_range}"

    
    def get_leaf_nodes_paths(self):
        paths = []
        hyp = []
        for node in nx.descendants(self.track_three, self.root):
            if self.track_three.out_degree(node) == 0:
                hyp.append(node)
                
                paths.append(nx.shortest_path(self.track_three, self.root, node))
                #delete root node
                paths[-1].remove(self.root)
                
        return paths,hyp

    def create_path_matrix(self):
        paths,hyp_nodes = self.get_leaf_nodes_paths()
        
        
        
        n_paths = len(paths)
        nodes = list(self.track_three.nodes())
        n_nodes = len(nodes)
        path_matrix = [[''] * n_nodes for _ in range(n_paths)]
        for i, path in enumerate(paths):
            for j, node in enumerate(path):
                formated = str(node)
                
                path_matrix[i][nodes.index(node)] = formated[2:]
        path_matrix = np.array(path_matrix)
        det = np.unique(path_matrix)
        arr_no_zero = det[np.char.find(det.astype(str), "zero") == -1]
        arr_no_zero = arr_no_zero[np.char.find(arr_no_zero.astype(str), self.root) == -1]
        
        arr_no_zero = arr_no_zero[1:]
       
        hypot = np.zeros((len(arr_no_zero),len(paths)))
        paths = np.array(paths)
        
        for i,det in enumerate(arr_no_zero):
            for j,path in enumerate(path_matrix):
                
                if np.any(np.char.find(path.astype(str), det) != -1):
                    hypot[i][j] = 1
                
        
        hyp_nodes_score = [self.track_three.nodes[n]["score"] for n in hyp_nodes]
        return hypot,hyp_nodes,arr_no_zero,hyp_nodes_score
    def draw_tree(self):
        print("Drawing")
        pos = nx.drawing.nx_agraph.graphviz_layout(self.track_three, prog='dot')
        node_labels = {node: str(node) for node in self.track_three.nodes()}
        nx.draw_networkx_nodes(self.track_three, pos, node_color='lightblue', node_size=1000)
        nx.draw_networkx_edges(self.track_three, pos)
        nx.draw_networkx_labels(self.track_three, pos, labels=node_labels, font_color='black')
        plt.axis('off')
        plt.show()
        
    
    def Pruning(self, leaf_node, n=2):
        # Get Nth parent of leaf_node
        
        parent = leaf_node
        try:
            for i in range(n):
                parent = next(self.track_three.predecessors(parent))
        except:
        
            return
        # Get all descendants of parent
        descendants = set(nx.descendants(self.track_three, parent))
        
        # Remove all nodes that are not the leaf node, the parent, or the parent's descendants
        nodes_to_remove = set(self.track_three.nodes()) - {leaf_node, parent} - descendants
        self.root = parent
        self.track_three.remove_nodes_from(nodes_to_remove)
    
    def get_leaf_nodes_paths_v2(self):
        descendants = nx.algorithms.descendants(self.track_three, self.root)
        leaf_nodes = [node for node in descendants if self.track_three.out_degree(node) == 0]
        paths = nx.shortest_path(self.track_three, self.root)
        leaf_paths = {node: path[1:] for node, path in paths.items() if node in leaf_nodes}
        return list(leaf_paths.values()), list(leaf_paths.keys())

    def create_path_matrix_v2(self):
        paths, hyp_nodes = self.get_leaf_nodes_paths()
        n_paths = len(paths)
        nodes = np.array(list(self.track_three.nodes()))
        path_matrix = np.char.mod('%d', np.tile(nodes, (n_paths, 1)))
        for i, path in enumerate(paths):
            path_matrix[i, ~np.isin(nodes, path)] = ''
        det = np.unique(path_matrix)
        arr_no_zero = det[(np.char.find(det.astype(str), "zero") == -1) & (np.char.find(det.astype(str), self.root) == -1)]
        arr_no_zero = arr_no_zero[1:]
        hypot = np.char.find(path_matrix[:, :, np.newaxis], arr_no_zero) != -1
        return hypot.astype(int), hyp_nodes, arr_no_zero

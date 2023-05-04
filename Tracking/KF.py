import numpy as np
from scipy.linalg import inv


class KalmanFilter(object):
    def __init__(self, dt, x_init, P_init, Q, R):
        self.dt = dt  # time step
        self.x = x_init  # initial state (position, velocity)
        self.P = P_init  # initial covariance matrix
        self.Q = Q  # process noise covariance
        self.R = R  # measurement noise covariance
        self.x_iso = np.array([0,0],dtype="float64")
        
        self.F = np.array([[1, self.dt], [0, 1]])  # state transition matrix
        #convert to ISO
        self.x_iso[0] = self.x[0]*0.785277
        self.x_iso[1] = (128-self.x[1])*-0.0656168
       
        

    def predict(self, u=None):
        
        if u is not None:
            B = np.array([[(self.dt**2)/2], [self.dt]])  # control input matrix
            self.x_iso = self.F @ self.x_iso + B @ u
                      
        else:
            
           
            self.x_iso = self.F @ self.x_iso
            self.convert_from_iso()
        self.P = self.F @ self.P @ self.F.T + self.Q

    def get_prediction(self):
        
        
                      
        pred = self.F @ self.x_iso
        #convert to cords
        pred[0]= pred[0]/0.785277
        pred[1] = 128+pred[1]/0.0656168
        
        return pred
            
        
    def convert_from_iso(self):
      
        self.x[0] = self.x_iso[0]/0.785277
        self.x[1] = 128+self.x_iso[1]/0.0656168
       
    def update(self, z):
        #covert to ISO
     
        z_iso = np.array((2,1),dtype="float64")
        z_iso[0] = z[0]*0.785277
        z_iso[1] = (128-z[1])*-0.0656168
        H = np.array([[1, 0], [0, 1]])  # observation matrix
       
        y = z_iso - H @ self.x_iso  # innovation
        
        self.S = H @ self.P @ H.T + self.R  # innovation covariance
        
        K = self.P @ H.T @ inv(self.S)  # Kalman gain
        
        
        self.x_iso = self.x_iso + K @ y  # updated state estimate
        self.convert_from_iso()
       
        
        self.P = (np.eye(2) - K @ H) @ self.P  # updated covariance matrix

    def nis(self, z,debug = False):
        #covert to ISO
        z_iso = np.array((2,1),dtype="float64")
        z_iso[0] = z[0]*0.785277
        z_iso[1] = (128-z[1])*-0.0656168
        
        #self.predict()
        H = np.array([[1, 0], [0, 1]])
        P = P = self.F @ self.P @ self.F.T + self.Q
        S = H @ P @ H.T + self.R
        K = self.P @ H.T @ np.linalg.inv(S)
        x_pred =self.F @ self.x_iso
        if debug:
            print("Before:",self.x_iso[0],self.x_iso[1])
            print("Measument",z_iso[0],z_iso[1])
            print("Pred",x_pred[0],x_pred[1])
            
        
        innovation = z_iso - H @ x_pred
        return innovation.T @ np.linalg.inv(S) @ innovation
    def __str__(self):
        return f"Range:{self.x_iso[0]}, V:{self.x_iso[1]}"
    
    

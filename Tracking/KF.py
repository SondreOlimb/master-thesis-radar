import numpy as np
from scipy.linalg import inv


class KalmanFilter(object):
    def __init__(self, dt, x_init, P_init, Q, R):
        self.dt = dt  # time step
        self.x = x_init  # initial state (position, velocity)
        self.P = P_init  # initial covariance matrix
        self.Q = Q  # process noise covariance
        self.R = R  # measurement noise covariance
        self.x_iso = np.array([0,0])
        
        self.F = np.array([[1, self.dt], [0, 1]])  # state transition matrix
        #convert to ISO
        self.x_iso[0] = self.x[0]*0.785277
        self.x_iso[1] = (128-self.x[1])*-0.12755
        assert self.x_iso[1] < 0, f"The velocity is posisitve: {self.x_iso}"
        

    def predict(self, u=None):
        #print("predict")
        #print(self.x_iso)
        # state transition matrix
        if u is not None:
            B = np.array([[(self.dt**2)/2], [self.dt]])  # control input matrix
            self.x_iso = self.F @ self.x_iso + B @ u
                      
        else:
            
           
            self.x_iso = self.F @ self.x_iso
            #print(self.x_iso)
            self.convert_from_iso()
        self.P = self.F @ self.P @ self.F.T + self.Q

    def get_prediction(self):
        
        
                      
        pred = self.F @ self.x_iso
        #convert to cords
        pred[0]= pred[0]/0.785277
        pred[1] = 128+pred[1]/0.12755
        assert self.x_iso[1] < 0, f"The velocity is posisitve: {self.x_iso}"
        assert pred[1] < 128, f"The velocity is posisitve: {pred[1]}"
        return pred
            
        
    def convert_from_iso(self):
        #print("convert")
        #print(self.x)
        self.x[0] = self.x_iso[0]/0.785277
        self.x[1] = 128+self.x_iso[1]/0.12755
        #print(self.x)
        #print("\n")
    def update(self, z):
        #covert to ISO
        #print("update",self.x_iso)
        z[0] = z[0]*0.785277
        z[1] = (128-z[1])*-0.12755
        H = np.array([[1, 0], [0, 1]])  # observation matrix
       
        y = z - H @ self.x_iso  # innovation
        
        self.S = H @ self.P @ H.T + self.R  # innovation covariance
        
        K = self.P @ H.T @ inv(self.S)  # Kalman gain
        
        assert abs(self.x_iso[0] -z[0]) < 10, f"RAnge delta to big: {self.x_iso}, {z}"
        self.x_iso = self.x_iso + K @ y  # updated state estimate
        self.convert_from_iso()
        #assert abs(self.x_iso[0] -z[0]) < 10, f"RAnge delta to big: {self.x_iso}, {z}"
        
        self.P = (np.eye(2) - K @ H) @ self.P  # updated covariance matrix

    def nis(self, z):
        #covert to ISO
       
        z[0] = z[0]*0.785277
        z[1] = (128-z[1])*-0.12755
        
        #self.predict()
        H = np.array([[1, 0], [0, 1]])
        P = P = self.F @ self.P @ self.F.T + self.Q
        S = H @ P @ H.T + self.R
        K = self.P @ H.T @ np.linalg.inv(S)
        x_pred =self.F @ self.x_iso
        
        innovation = z - H @ x_pred
        return innovation.T @ np.linalg.inv(S) @ innovation
    def __str__(self):
        return f"Range:{self.x_iso[0]}, V:{self.x_iso[1]}"
    
    

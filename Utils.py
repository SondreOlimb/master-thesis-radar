from scipy.signal import detrend
import numpy as np
import time

def read_RADC(data,length,save=False):
    
                    
   
    data_RADC = np.frombuffer(data,dtype=np.uint16)
    data_RADC = data_RADC.reshape(3,256,512)
    data_RADC_I_raw = data_RADC[:,:,::2]
    data_RADC_Q_raw = data_RADC[:,:,1::2]
    data_RADC_I = detrend(data_RADC_I_raw, axis=2)
    data_RADC_Q = detrend(data_RADC_Q_raw, axis=2)
                    
    data_RADC_I_mean = data_RADC_I
    data_RADC_Q_mean = data_RADC_Q
    data_proc =data_RADC_I_mean[0,:,:] + 1j*data_RADC_Q_mean[0,:,:]
    if save:
        np.save(f"data/RADC/{time.time_ns()}.npy",data_proc)
    return data_proc

def read_PPRM(data):
    data_PPRM = np.frombuffer(data,dtype=np.uint16)
    print(data_PPRM)


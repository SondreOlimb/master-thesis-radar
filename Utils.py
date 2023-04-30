from scipy.signal import detrend
import numpy as np
import time
import logging

def read_RADC(data,length,save=False):
    if save:
        np.save(f"data/RADC_BIN/{time.time_ns()}.npy",data)
                    
   
    data_RADC = np.frombuffer(data,dtype=np.uint16)
    
    data_RADC = data_RADC.reshape(3,256,512)
    data_RADC_I_raw = data_RADC[:,:,::2]
    data_RADC_Q_raw = data_RADC[:,:,1::2]
    data_RADC_I = detrend(data_RADC_I_raw, axis=2).astype(np.float16)
    data_RADC_Q = detrend(data_RADC_Q_raw, axis=2).astype(np.float16)
                    
    data_RADC_I_mean = data_RADC_I
    data_RADC_Q_mean = data_RADC_Q
    data_proc =data_RADC_I_mean[0,:,:] + 1j*data_RADC_Q_mean[0,:,:]
    data_proc = data_proc
    
    return data_proc

def read_PPRM(data):
    data_PPRM = np.frombuffer(data,dtype=np.uint16)
    logging.warning(data_PPRM)


from scipy.signal import detrend
import numpy as np
def read_RADC(data,length):
    
                    
   
    data_RADC = np.frombuffer(data,dtype=np.uint16)
    data_RADC = data_RADC.reshape(3,256,512)
    data_RADC_I_raw = data_RADC[:,:,::2]
    data_RADC_Q_raw = data_RADC[:,:,1::2]
    data_RADC_I = detrend(data_RADC_I_raw, axis=2)
    data_RADC_Q = detrend(data_RADC_Q_raw, axis=2)
                    
    data_RADC_I_mean = data_RADC_I
    data_RADC_Q_mean = data_RADC_Q
    
    return data_RADC_I_mean[0,:,:] + 1j*data_RADC_Q_mean[0,:,:]

def read_PPRM(data):
    data_PPRM = np.frombuffer(data,dtype=np.uint16)
    print(data_PPRM)
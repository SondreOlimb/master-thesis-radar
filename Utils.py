from scipy.signal import detrend
import numpy as np
import time
import logging
import requests

def read_RADC(data,length,save=False):
    if save:
        np.save(f"data/RADC_BIN/{time.time_ns()}.npy",data)
                    
   
    data_RADC = np.frombuffer(data[:262144],dtype=np.uint16)
    
    data_RADC = data_RADC.reshape(256,512)
    
    data_RADC_I_raw = data_RADC[:,::2]
   
    data_RADC_Q_raw = data_RADC[:,1::2]
   
    data_RADC_I = detrend(data_RADC_I_raw, axis=1)
    data_RADC_Q = detrend(data_RADC_Q_raw, axis=1)
                    
   
    data_proc =data_RADC_I + 1j*data_RADC_Q
   
    
    return data_proc

def read_PPRM(data):
    data_PPRM = np.frombuffer(data,dtype=np.uint16)
    logging.warning(data_PPRM)



def check_internet_connection():
    try:
        # Send a request to a known website
        requests.get('https://www.google.com')
        return True
    except:
        # If the request fails, assume no internet connection
        logging.warning("No internett")
        return False


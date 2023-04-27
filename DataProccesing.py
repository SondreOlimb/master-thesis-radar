import numpy as np
import struct
import time
from scipy.signal import detrend
import logging
def read_TDAT(data):
    data_arr = []
    for i in range(0,data["length"],44):
        id = int.from_bytes(data["data"][i:4],byteorder="little", signed=False)
        life = int.from_bytes(data["data"][i+4:i+8],byteorder="little", signed=False)
        est_range =round(struct.unpack("f",data["data"][i+8:i+12])[0]*0.157,2)#0.785277
        est_speed = round(struct.unpack("f",data["data"][i+12:i+16])[0]*0.127552440715,2)
        if(est_speed<0):
            data_arr.append({"id":int(id),
            "range":est_range,
            "speed":est_speed,
            "life":life

            } )
    if len(data_arr)==0: return 0
    return {int(time.time()):data_arr}
    

def read_PPRM(data):
    PPRM = {
        "PSPT":int.from_bytes(data["data"][0:4],byteorder="little", signed=False), #Processor peak detection threshold
        "PSNP":int.from_bytes(data["data"][10:12],byteorder="little", signed=False),#Processor maximum number of peaks
        "PSRC":round(struct.unpack("f",data["data"][12:16])[0],2), #Processor range compensation for threshold
        "PSBR":int.from_bytes(data["data"][16:18],byteorder="little", signed=False),#Processor peak detection minimum range
        "PSTR":int.from_bytes(data["data"][18:20],byteorder="little", signed=False),#Processor peak detection maximum range
        "PSBS":int.from_bytes(data["data"][20:22],byteorder="little", signed=False), #Processor peak detection minimum speed
        "PSTS" :int.from_bytes(data["data"][22:24],byteorder="little", signed=False), #Processor peak detection maximum speed
        "PSSM":int.from_bytes(data["data"][24:26],byteorder="little", signed=False), #Processor smooth mean range-doppler map
        "PSNT":int.from_bytes(data["data"][28:30],byteorder="little", signed=False), #Processor maximum number of tracks to report
        "PSRJ":int.from_bytes(data["data"][30:32],byteorder="little", signed=False), #Processor maximum range jitter
        "PSSJ":int.from_bytes(data["data"][32:34],byteorder="little", signed=False), #Processor maximum speed jitter
        "PSBL":int.from_bytes(data["data"][34:36],byteorder="little", signed=False), #Processor minimum track life 
        "PSTL":int.from_bytes(data["data"][36:38],byteorder="little", signed=False), #Processor maximum track life
        "PSTH":int.from_bytes(data["data"][40:42],byteorder="little", signed=False), #Processor length of history for tracking
        "PSSO":int.from_bytes(data["data"][42:44],byteorder="little", signed=False), #Processor report stationary objects
        "PSCS":int.from_bytes(data["data"][44:46],byteorder="little", signed=False), #Processor assume constant speed for tracking
        

    }
    
def read_RPRM(data):
    RPRM = {
        "RSID":int.from_bytes(data["data"][0:2],byteorder="little", signed=False), #Radar initial delay
        "RSSF":int.from_bytes(data["data"][2:4],byteorder="little", signed=False),#Radar start frequency
        "RSBW":int.from_bytes(data["data"][4:6],byteorder="little", signed=False),# Radar bandwidth
        "RSRG":int.from_bytes(data["data"][6:8],byteorder="little", signed=False),# Radar reciver gain

    }

def read_RADC(data,debug= False):
    length = data["length"]
                    
    data_RADC = data["data"][8:8+length]
    data_RADC = np.frombuffer(data_RADC,dtype=np.uint16)
    data_RADC = data_RADC.reshape(3,256,512)
    data_RADC_I_raw = data_RADC[:,:,::2]
    data_RADC_Q_raw = data_RADC[:,:,1::2]
    data_RADC_I = detrend(data_RADC_I_raw, axis=2)
    data_RADC_Q = detrend(data_RADC_Q_raw, axis=2)
                    
    data_RADC_I_mean = data_RADC_I
    data_RADC_Q_mean = data_RADC_Q
    procesed_data = data_RADC_I_mean[:,:,:] + 1j*data_RADC_Q_mean[:,:,:]
    if debug:
        t = time.localtime()
        timestamp = time.strftime('%b-%d-%Y_%H%M', t)
        np.save(f"RADC/RADC-{timestamp}-{time.time_ns()}")
    return procesed_data
    
    
    

def data_processing(data_queue,raw_data_queue,debug =False):
    print("Started data processing")
    while True:
        try:
        
            data = data_queue.get()
            logging.info(f"KMD7:{data_queue.qsize()}")
            if(data["type"]== "RADC" and data["length"] >1 ):
                data_RADC = read_RADC(data,debug)
                
                if data_RADC:
                    #detection_queue.put(tracking_data)
                    raw_data_queue.put(data_RADC)
                    
                    
        except KeyboardInterrupt:
            print("Exited data processing")
            break 
    return        

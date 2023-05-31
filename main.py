import multiprocessing as mp
import client
import data_processing
from SignalProcessingProcess import SPP
from TrackingProcess import TrackingProcess
import backend
import firebase
import time
# from geopy.geocoders import Nominatim
import logging_utils
import logging
from Utils import check_internet_connection
radar_settings = {
    "40":0.15705541,
     
    "70":0.27498872,
    "100":0.39263853,
    "150":0.59047965,
    "200":0.78527706,
    "250":0.9765625
}

if __name__ == "__main__":
    logging.info('Starting radar system')
    exit_event = mp.Event() #
    

    try:
        try:
            parameters = firebase.ref.child("parameters").get()
            settings = firebase.ref.child("settings").get()
            info = firebase.ref.child("info").get()
        except:
            logging.warning("Firabse lost connection")
        data_queue =  mp.Queue(maxsize=1)
        SP_data_queue = mp.Queue(maxsize=1)
        tracking_queue = mp.Queue()
        backend_queue = mp.Queue()
        r ="range"
        v ="speed"
        gain = "RSRG"
        logging.warning(f"Range: {info[r]} Velocity:{info[v]} Gain: {settings[gain]}")

        data_fetch = mp.Process(target=client.fetch_data, args=(exit_event,data_queue,parameters,settings,False))
        data_process = mp.Process(target=SPP, args=(exit_event,data_queue,SP_data_queue,radar_settings[info[r]],))
        tracking_process = mp.Process(target=TrackingProcess, args=(exit_event,SP_data_queue,tracking_queue,radar_settings[info[r]],))
        #data_backend = mp.Process(target=backend.backend, args=(tracking_queue,))
       
        

        data_fetch.start()
        data_process.start()
        tracking_process.start()
        #data_backend.start()
        
        while not exit_event.is_set():
            
                #if check_internet_connection():
                    firebase.ref.child("info").update({"status": "running"})
                    firebase.ref.child("info").update({"time": time.time()})
                    logging.info("Online")
                    time.sleep(60)
            
            
            

        logging.critical("System online")

    except KeyboardInterrupt: 
        exit_event.set() # Set the exit event to signal the child processes to exit

        data_fetch.join()
        data_process.join()
        tracking_process.join()
        #data_backend.join()
        logging.warning('Exited radar system with keyboard KeyboardInterrupt')
        try:
            #if check_internet_connection():
                firebase.ref.child("info").update({"status": "offline"})
        except:
            logging.warning("Firabse lost connection")
        pass
        
      



        
        
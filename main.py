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

if __name__ == "__main__":
    logging.info('Starting radar system')
    exit_event = mp.Event() #

    try:
        parameters = firebase.ref.child("parameters").get()
        settings = firebase.ref.child("settings").get()
        info = firebase.ref.child("info").get()
        data_queue = mp.Queue()
        SP_data_queue = mp.Queue()
        tracking_queue = mp.Queue()
        backend_queue = mp.Queue()
        r ="range"
        v ="speed"
        gain = "RSRG"
        logging.warning(f"Range: {info[r]} Velocity:{info[v]} Gain: {settings[gain]}")

        data_fetch = mp.Process(target=client.fetch_data, args=(exit_event,data_queue,parameters,settings,False))
        data_process = mp.Process(target=SPP, args=(exit_event,data_queue,SP_data_queue,))
        tracking_process = mp.Process(target=TrackingProcess, args=(exit_event,SP_data_queue,tracking_queue,info[r],))
        #data_backend = mp.Process(target=backend.backend, args=(tracking_queue,))
       
        

        data_fetch.start()
        data_process.start()
        tracking_process.start()
        #data_backend.start()
        while not exit_event.is_set():
            firebase.ref.child("info").update({"status": "running"})
            firebase.ref.child("info").update({"time": time.time()})
            logging.critical("Online")
            time.sleep(60)
            
            



    except KeyboardInterrupt: 
        exit_event.set() # Set the exit event to signal the child processes to exit

        data_fetch.join()
        data_process.join()
        tracking_process.join()
        #data_backend.join()
        logging.warning('Exited radar system with keyboard KeyboardInterrupt')
        firebase.ref.child("info").update({"status": "offline"})
        pass
        
      



        
        
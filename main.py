import multiprocessing as mp
import client
import data_processing
from SignalProcessingProcess import SPP
from TrackingProcess import TrackingProcess
import backend
import firebase
from geopy.geocoders import Nominatim
import time


if __name__ == "__main__":

    try:
        data_queue = mp.Queue()
        SP_data_queue = mp.Queue()
        tracking_queue = mp.Queue()
        backend_queue = mp.Queue()

        data_fetch = mp.Process(target=client.fetch_data, args=(data_queue,))
        data_process = mp.Process(target=SPP, args=(data_queue,SP_data_queue,))
        tracking_process = mp.Process(target=TrackingProcess, args=(SP_data_queue,tracking_queue,))
        #data_backend = mp.Process(target=backend.backend, args=(tracking_queue,))
       
        loc = Nominatim(user_agent="GetLoc")
        getLoc = loc.geocode("Trondheim")
        firebase.ref.child("info").update({"lat": getLoc.latitude})
        firebase.ref.child("info").update({"lng": getLoc.longitude})

        data_fetch.start()
        data_process.start()
        tracking_process.start()
        #data_backend.start()
        while True:
            firebase.ref.child("info").update({"status": "running"})
            firebase.ref.child("info").update({"time": time.time()})
            time.sleep(60)
            
            



    except KeyboardInterrupt:   
        data_fetch.join()
        data_process.join()
        data_backend.join()
        print('Keyboard interrupt received from user')
        firebase.ref.child("info").update({"status": "offline"})
        pass
        
        # data_process.close()
        # data_fetch.close()
        # data_backend.close()



        
        
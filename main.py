import multiprocessing as mp
import client
import data_processing
import backend
import os
import sys

if __name__ == "__main__":

    try:
        data_queue = mp.Queue()
        detection_queue = mp.Queue()
        backend_queue = mp.Queue()

        data_fetch = mp.Process(target=client.fetch_data, args=(data_queue,))
        data_process = mp.Process(target=data_processing.data_processing, args=(data_queue,detection_queue,))
        data_backend = mp.Process(target=backend.backend, args=(detection_queue,))
     

        data_fetch.start()
        data_process.start()
        data_backend.start()
        data_fetch.join()
        data_process.join()
        data_backend.join()


    except KeyboardInterrupt:   
        print('Keyboard interrupt received from user')
        pass
        
        # data_process.close()
        # data_fetch.close()
        # data_backend.close()



        
        
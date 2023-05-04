from SignalProcessing.main import SignalProcesingAlgorithem,Artifacts
import logging
import time
import numpy as np
def SPP(exit_event,data_queue,detection_queue,range_setting):
    logging.info("Started SignalProvesing")
    # Path: SignalProcessingProcess.py
    # Function: SignalProcesing
    # Input: signal
    # Output: signal
    # Description: This function is used to process the signalq
    artifacts = None
    time_arr = []
    drop_count = 1
    while not exit_event.is_set():
        data = data_queue.get()
        drop_count += data[0]
        data = data[1]
        if data_queue.qsize() > 5:
            logging.error(f"Data fetch queue: {data_queue.qsize()}")
        if detection_queue.qsize() > 5:
            logging.error(f"SP queue: {detection_queue.qsize()}")
        if data is not None:
            #start = time.time()
            if artifacts is None:
                artifacts = Artifacts(data)
            
            else:
                if  detection_queue.empty():
                    detection_queue.put((drop_count,SignalProcesingAlgorithem(data,artifacts,range_setting)) )
                    drop_count =1
                else:
                    drop_count +=1
            end = time.time()
            #time_arr.append(end-start)

            #logging.info(f"SP: Mean{np.mean(time_arr)},STD: {np.std(time_arr)}")
   


   
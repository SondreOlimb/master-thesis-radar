from SignalProcessing.main import SignalProcesingAlgorithem,Artifacts
import logging
def SPP(exit_event,data_queue,detection_queue):
    logging.info("Started SignalProvesing")
    # Path: SignalProcessingProcess.py
    # Function: SignalProcesing
    # Input: signal
    # Output: signal
    # Description: This function is used to process the signalq
    artifacts = None
    while not exit_event.is_set():
        data = data_queue.get()
        if data_queue.qsize() > 5:
            logging.error(f"Data fetch queue: {data_queue.qsize()}")
        if detection_queue.qsize() > 5:
            logging.error(f"SP queue: {detection_queue.qsize()}")
        if data is not None:
            
            if artifacts is None:
                artifacts = Artifacts(data)
            
            else:
                
                detection_queue.put(SignalProcesingAlgorithem(data,artifacts) )
      

   


   
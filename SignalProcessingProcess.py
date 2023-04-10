from SignalProcessing.main import SignalProcesingAlgorithem,Artifacts

def SPP(data_queue,detection_queue):
    print("Started SignalProvesing")
    # Path: SignalProcessingProcess.py
    # Function: SignalProcesing
    # Input: signal
    # Output: signal
    # Description: This function is used to process the signalq
    artifacts = None
    while True:
        data = data_queue.get()
        if data is not None:
            
            if artifacts is None:
                artifacts = Artifacts(data)
            
            else:
                
                detection_queue.put(SignalProcesingAlgorithem(data,artifacts) )
           

   


   
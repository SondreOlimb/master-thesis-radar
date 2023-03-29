from SignalProcessing.main import SignalProcesingAlgorithem,Artifacts

def SPP(data_queue,detection_queue):
    # Path: SignalProcessingProcess.py
    # Function: SignalProcesing
    # Input: signal
    # Output: signal
    # Description: This function is used to process the signalq
    artifacts = None
    while True:
        data = data_queue.get()
        if data is not None:
            print("started SP")
            if artifacts is None:
                artifacts = Artifacts(data)
            
            else:
                detection_queue.put( SignalProcesingAlgorithem(data[0],artifacts))
            print("finished SP")

   


   
from SignalProcessing.main import SignalProcesingAlgorithem,Artifacts

def SignalProcessing(data_queue,detection_queue):
    # Path: SignalProcessingProcess.py
    # Function: SignalProcesing
    # Input: signal
    # Output: signal
    # Description: This function is used to process the signalq
    artifacts = None
    while True:
        data = data_queue.get()
        if data is not None:
            artifacts = Artifacts(data)
        else:
             detection_queue.put( SignalProcesingAlgorithem(data[0],artifacts))


   


   
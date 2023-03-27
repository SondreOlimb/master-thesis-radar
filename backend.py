import firebase

def backend(detection_queue):
    print("Started backend") 
    while True:
        try:
            data = detection_queue.get()
            if data:
                print(data[1])
                firebase.ref.child(f'detections/{data[0]}').set(data[1])
        except KeyboardInterrupt:
            print("Exited data backend")
            break
            
    
    return
            
    


    
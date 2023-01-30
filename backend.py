import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import json

import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("radar-a90c0-firebase-adminsdk-rbwyb-294c210c78.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://radar-a90c0-default-rtdb.europe-west1.firebasedatabase.app"
})
ref = db.reference('/radar')

def backend(detection_queue):
    print("Started backend") 
    while True:
        try:
            data = detection_queue.get()
            if data:
                print(data)
                
                # for det in list((data.values()))[0] :
            
                #     print("ID:",det["id"] ,"Speed: ",det["speed"],"Range: ",det["range"])
                ref.child('detections').set(data)
        except KeyboardInterrupt:
            print("Exited data backend")
            break
            
    
    return
            
    


    
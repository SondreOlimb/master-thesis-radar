import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import json

import firebase_admin
from firebase_admin import credentials


cred = credentials.Certificate("radar-a90c0-firebase-adminsdk-rbwyb-294c210c78.json")
firebase_app = firebase_admin.initialize_app(cred, {
    'databaseURL': "https://radar-a90c0-default-rtdb.europe-west1.firebasedatabase.app"
})
ref = db.reference('/radar')
logs = db.reference('/radar/logs')
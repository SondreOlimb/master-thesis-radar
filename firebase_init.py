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

ref_settings = db.reference('/radar/settings')
data_parameters ={'PSPT': 1000, 'PSNP': 128, 'PSRC': 0.0, 'PSBR': 2, 'PSTR': 200, 'PSBS': 0, 'PSTS': 100, 'PSSM': 1, 'PSNT': 11, 'PSRJ': 2, 'PSSJ': 3, 'PSBL': 5, 'PSTL': 15, 'PSTH': 10, 'PSSO': 0, 'PSCS': 1}
data_settings ={'RSID': 11106, 'RSSF': 23800, 'RSBW': 970, 'RSRG': 10}
ref.child('parameters').set(data_parameters)
ref.child('settings').set(data_settings)

            
    


    
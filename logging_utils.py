import logging

from Utils import check_internet_connection

import firebase
class FirebaseHandler(logging.Handler):
    def emit(self, record):
        if record.levelno >= logging.ERROR:
            log_entry = self.format(record)
            try:
                #if check_internet_connection():
                    firebase.logs.push().set(log_entry)
                #else:
                 #   logging.warning("No internett")
            except:
                logging.warning("Firabase lost connection")
# Initialize Firebase app

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    handlers=[logging.StreamHandler(), logging.FileHandler('logfile.log'),FirebaseHandler()])
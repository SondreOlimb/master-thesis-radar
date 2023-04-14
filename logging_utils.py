import logging



import firebase
class FirebaseHandler(logging.Handler):
    def emit(self, record):
        if record.levelno >= logging.ERROR:
            log_entry = self.format(record)
            firebase.logs.push().set(log_entry)
# Initialize Firebase app

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    handlers=[logging.StreamHandler(), logging.FileHandler('logfile.log'),FirebaseHandler()])
# cleaner.py

from lockbox.database import init_db, db_session
from lockbox.models import File
from time import sleep
import datetime

# Initialise Database Connection
init_db()

# Set timeout, 10 seconds
timeout = 10.0

def clean():
    while True:
        # Open database
        files = File.query.all()
        for file in files:
            period = (datetime.datetime.now() - file.created_date).total_seconds()
            if period >= file.file_timeout_duration:
                print("Found timed out file", file.file_name)
                File.query.filter(File.id == file.id).delete()
                print("Deleted file", file.file_name)

            db_session.commit()
            
        sleep(timeout)

if __name__ == "__main__":
    clean()
# models.py

import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from .database import Base

class File(Base):
    __tablename__ = 'Files'
    id = Column(Integer, primary_key=True)
    file_name = Column(String(120))
    file_type = Column(String(120))
    file_size = Column(Integer)
    file_upload_time = Column(DateTime)
    file_timeout_duration = Column(Integer)
    file_passcode_hash = Column(String)
    file_path = Column(String)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, file_name=None, file_type=None, file_size=None, file_path=None,
                 file_timeout_duration=None, file_passcode_hash=None, created_date=None):
        self.file_name = file_name
        self.file_type = file_type
        self.file_size = file_size
        self.file_path = file_path
        self.file_timeout_duration = file_timeout_duration
        self.file_passcode_hash = file_passcode_hash
        self.created_date = created_date

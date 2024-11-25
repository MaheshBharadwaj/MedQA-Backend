import uuid
from datetime import datetime
from src.utils.db import db

# Message-File association table
message_files = db.Table('message_files',
    db.Column('message_id', db.UUID(as_uuid=True), db.ForeignKey('messages.message_id'), primary_key=True),
    db.Column('file_id', db.UUID(as_uuid=True), db.ForeignKey('files.file_id'), primary_key=True)
)

class File(db.Model):
    __tablename__ = 'files'

    file_id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_name = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    s3_key = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.user_id'), nullable=False)

    def __init__(self, file_name, file_type, file_size, s3_key, user_id):
        self.file_name = file_name
        self.file_type = file_type
        self.file_size = file_size
        self.s3_key = s3_key
        self.user_id = user_id

    def to_dict(self):
        return {
            'file_id': str(self.file_id),
            'file_name': self.file_name,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'uploaded_at': self.uploaded_at.isoformat()
        }
import uuid
from datetime import datetime
from src.utils.db import db

class Message(db.Model):
    __tablename__ = 'messages'

    message_id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('chats.chat_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    tokens_used = db.Column(db.Integer)

    # Relationships
    files = db.relationship('File', secondary='message_files', backref='messages')

    def __init__(self, chat_id, content, role, tokens_used=None):
        self.chat_id = chat_id
        self.content = content
        self.role = role
        self.tokens_used = tokens_used

    def to_dict(self, include_files=False):
        message_dict = {
            'message_id': str(self.message_id),
            'chat_id': str(self.chat_id),
            'content': self.content,
            'role': self.role,
            'timestamp': self.timestamp.isoformat(),
            'tokens_used': self.tokens_used
        }
        
        if include_files:
            message_dict['files'] = [file.to_dict() for file in self.files]
        
        return message_dict
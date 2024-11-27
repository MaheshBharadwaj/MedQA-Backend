import uuid
from datetime import datetime
from src.utils.db import db
from src.config.constants import ModelProvider

class Chat(db.Model):
    __tablename__ = 'chats'

    chat_id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.user_id'), nullable=False)
    model_type = db.Column(db.String(50), nullable=False)

    # Relationships
    messages = db.relationship('Message', backref='chat', lazy=True, cascade='all, delete-orphan')

    def __init__(self, title, user_id, model_type):
        self.title = title
        self.user_id = user_id
        if model_type not in ModelProvider.list():
            raise ValueError(f"Invalid model type. Must be one of {ModelProvider.list()}")
        self.model_type = model_type

    def to_dict(self):
        return {
            'chat_id': str(self.chat_id),
            'title': self.title,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'model_type': self.model_type,
            'last_message': self.get_last_message()
        }

    def get_last_message(self):
        last_message = (Message.query
                       .filter_by(chat_id=self.chat_id)
                       .order_by(Message.timestamp.desc())
                       .first())
        if last_message:
            return {
                'content': last_message.content,
                'timestamp': last_message.timestamp.isoformat()
            }
        return None
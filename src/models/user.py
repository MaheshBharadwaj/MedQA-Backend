import uuid
from datetime import datetime
from src.utils.db import db

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    organization = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    last_login = db.Column(db.DateTime(timezone=True))

    # Relationships
    chats = db.relationship('Chat', backref='user', lazy=True)
    files = db.relationship('File', backref='user', lazy=True)

    def to_dict(self):
        return {
            'user_id': str(self.user_id),
            'email': self.email,
            'name': self.name,
            'organization': self.organization,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

    def update_last_login(self):
        self.last_login = datetime.utcnow()
        db.session.commit()
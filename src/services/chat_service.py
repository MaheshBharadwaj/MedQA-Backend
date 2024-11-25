from src.models.chat import Chat
from src.models.message import Message
from src.utils.db import db
from src.utils.exceptions import ResourceNotFoundError, ValidationError
from src.config.constants import ModelProvider
from datetime import datetime

class ChatService:
    @staticmethod
    def create_chat(user_id, title, model_type):
        if model_type not in ModelProvider.list():
            raise ValidationError(f"Invalid model type. Must be one of {ModelProvider.list()}")
        
        chat = Chat(
            title=title,
            user_id=user_id,
            model_type=model_type
        )
        db.session.add(chat)
        db.session.commit()
        return chat

    @staticmethod
    def get_chat(chat_id, user_id):
        chat = Chat.query.filter_by(chat_id=chat_id, user_id=user_id).first()
        if not chat:
            raise ResourceNotFoundError("Chat not found")
        return chat

    @staticmethod
    def get_user_chats(user_id, limit=20, offset=0, sort="created_at:desc"):
        field, direction = sort.split(':')
        order = getattr(getattr(Chat, field), 'desc' if direction == 'desc' else 'asc')()
        
        query = Chat.query.filter_by(user_id=user_id).order_by(order)
        total = query.count()
        chats = query.offset(offset).limit(limit).all()
        
        return {
            'chats': [chat.to_dict() for chat in chats],
            'total': total,
            'has_more': total > (offset + limit)
        }

    @staticmethod
    def add_message(chat_id, content, role, files=None, tokens_used=None):
        message = Message(
            chat_id=chat_id,
            content=content,
            role=role,
            tokens_used=tokens_used
        )
        
        if files:
            message.files.extend(files)
        
        db.session.add(message)
        
        # Update chat's updated_at timestamp
        chat = Chat.query.get(chat_id)
        chat.updated_at = datetime.utcnow()
        
        db.session.commit()
        return message

    @staticmethod
    def get_messages(chat_id, limit=50, before=None, include_files=False):
        query = Message.query.filter_by(chat_id=chat_id)
        
        if before:
            before_message = Message.query.get(before)
            if before_message:
                query = query.filter(Message.timestamp < before_message.timestamp)
        
        messages = query.order_by(Message.timestamp.desc()).limit(limit).all()
        
        return {
            'messages': [msg.to_dict(include_files=include_files) for msg in messages],
            'has_more': len(messages) == limit
        }

    @staticmethod
    def delete_chat(chat_id, user_id):
        chat = ChatService.get_chat(chat_id, user_id)
        db.session.delete(chat)
        db.session.commit()
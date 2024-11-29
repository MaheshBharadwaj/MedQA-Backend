from src.models.chat import Chat
from src.models.message import Message
from src.utils.db import db
from src.utils.exceptions import ResourceNotFoundError, ValidationError
from src.config.constants import ModelProvider
from datetime import datetime
from typing import Optional, Dict, List
from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError

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

    def append_message(
        chat_id: UUID,
        content: str,
        role: str,
        files: Optional[List] = None
    ) -> Optional[Dict]:
        """
        Append a new message to a chat.
        
        Args:
            chat_id (UUID): The ID of the chat to append the message to
            content (str): The content of the message
            role (str): The role of the message sender
            files (List, optional): List of file objects to attach to the message
            
        Returns:
            Dict: The created message as a dictionary, or None if creation fails
        """
        try:
            message = Message(
                chat_id=chat_id,
                content=content,
                role=role
            )
            
            db.session.add(message)
            db.session.commit()
            
            return message.to_dict(include_files=True)
            
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Failed to append message: {str(e)}")
            
    @staticmethod
    def get_chat_messages(
        chat_id: UUID,
        include_files: bool = False
    ) -> List[Dict]:
        """
        Retrieve all messages for a specific chat.
        
        Args:
            chat_id (UUID): The ID of the chat to get messages from
            include_files (bool): Whether to include file information in the response
            
        Returns:
            List[Dict]: List of messages as dictionaries
        """
        try:
            messages = Message.query.filter_by(chat_id=chat_id)\
                                 .order_by(Message.timestamp.asc())\
                                 .all()
            
            return [msg.to_dict(include_files=include_files) for msg in messages]
            
        except SQLAlchemyError as e:
            raise Exception(f"Failed to retrieve chat messages: {str(e)}")
            
    @staticmethod
    def delete_chat(chat_id, user_id):
        chat = ChatService.get_chat(chat_id, user_id)
        db.session.delete(chat)
        db.session.commit()
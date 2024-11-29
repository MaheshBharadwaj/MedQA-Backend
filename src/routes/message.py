from flask import Blueprint, jsonify, request
from typing import Dict, Any
from uuid import UUID
from http import HTTPStatus
from src.services.chat_service import ChatService

message_bp = Blueprint('messages', __name__)

@message_bp.route('/chats/<uuid:chat_id>/messages', methods=['POST'])
def append_message(chat_id: UUID) -> tuple[Dict[str, Any], int]:
    """
    Append a new message to a chat.
    
    Args:
        chat_id (UUID): The ID of the chat to append the message to
        
    Returns:
        tuple: (response_data, status_code)
    """
    try:
        data = request.get_json()
        
        if not all(key in data for key in ['content', 'role']):
            return jsonify({
                'error': 'Missing required fields. Required: content, role'
            }), HTTPStatus.BAD_REQUEST
            
        message = ChatService.append_message(
            chat_id=chat_id,
            content=data['content'],
            role=data['role'],
            files=data.get('files')
        )
        
        return jsonify(message), HTTPStatus.CREATED
        
    except Exception as e:
        print(e)
        return jsonify({
            'error': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@message_bp.route('/chats/<uuid:chat_id>/messages', methods=['GET'])
def get_chat_messages(chat_id: UUID) -> tuple[Dict[str, Any], int]:
    """
    Get all messages in a chat.
    
    Args:
        chat_id (UUID): The ID of the chat to get messages from
        
    Returns:
        tuple: (response_data, status_code)
    """
    try:
        include_files = request.args.get('include_files', 'false').lower() == 'true'
        messages = ChatService.get_chat_messages(
            chat_id=chat_id,
            include_files=include_files
        )
        
        return jsonify({
            'chat_id': str(chat_id),
            'messages': messages
        }), HTTPStatus.OK
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

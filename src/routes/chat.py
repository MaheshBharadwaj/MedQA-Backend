from flask import Blueprint, request, jsonify
from src.services.chat_service import ChatService
from src.utils.decorators import require_auth
from src.utils.exceptions import ValidationError, ResourceNotFoundError
from src.config.constants import StatusCodes, Messages

chat_bp = Blueprint('chat', __name__, url_prefix='/chats')

@chat_bp.route('', methods=['POST'])
@require_auth
def create_chat(current_user):
    try:
        data = request.get_json()
        if not data or 'title' not in data or 'model_type' not in data:
            raise ValidationError("Missing required fields")

        chat = ChatService.create_chat(
            user_id=current_user.user_id,
            title=data['title'],
            model_type=data['model_type']
        )

        return jsonify(chat.to_dict()), StatusCodes.CREATED

    except ValidationError as e:
        return jsonify({
            'error': {
                'code': 'INVALID_REQUEST',
                'message': str(e)
            }
        }), StatusCodes.BAD_REQUEST
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': Messages.SERVER_ERROR
            }
        }), StatusCodes.INTERNAL_ERROR

@chat_bp.route('', methods=['GET'])
@require_auth
def get_chats(current_user):
    try:
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        sort = request.args.get('sort', 'created_at:desc')

        result = ChatService.get_user_chats(
            user_id=current_user.user_id,
            limit=limit,
            offset=offset,
            sort=sort
        )

        return jsonify(result), StatusCodes.OK

    except Exception as e:
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': Messages.SERVER_ERROR
            }
        }), StatusCodes.INTERNAL_ERROR

@chat_bp.route('/<uuid:chat_id>', methods=['GET'])
@require_auth
def get_chat(current_user, chat_id):
    try:
        chat = ChatService.get_chat(chat_id, current_user.user_id)
        return jsonify(chat.to_dict()), StatusCodes.OK

    except ResourceNotFoundError as e:
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': str(e)
            }
        }), StatusCodes.NOT_FOUND
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': Messages.SERVER_ERROR
            }
        }), StatusCodes.INTERNAL_ERROR

@chat_bp.route('/<uuid:chat_id>', methods=['DELETE'])
@require_auth
def delete_chat(current_user, chat_id):
    try:
        ChatService.delete_chat(chat_id, current_user.user_id)
        return '', StatusCodes.OK

    except ResourceNotFoundError as e:
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': str(e)
            }
        }), StatusCodes.NOT_FOUND
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': Messages.SERVER_ERROR
            }
        }), StatusCodes.INTERNAL_ERROR
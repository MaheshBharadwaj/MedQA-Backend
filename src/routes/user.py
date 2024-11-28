from flask import Blueprint, request, jsonify
from src.services.user_service import UserService
from src.utils.decorators import require_auth
from src.utils.exceptions import ValidationError, ResourceNotFoundError
from src.config.constants import StatusCodes, Messages

user_bp = Blueprint('user', __name__, url_prefix='/users')

@user_bp.route('', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        if not data or 'email' not in data or 'name' not in data:
            raise ValidationError("Missing required fields")

        user = UserService.create_user(
            email=data['email'],
            name=data['name'],
            organization=data.get('organization')
        )

        return jsonify(user.to_dict()), StatusCodes.CREATED

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

@user_bp.route('/<uuid:user_id>', methods=['GET'])
@require_auth
def get_user(current_user, user_id):
    try:
        user = UserService.get_user_by_id(user_id)
        return jsonify(user.to_dict()), StatusCodes.OK

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

@user_bp.route('/<uuid:user_id>', methods=['PUT'])
@require_auth
def update_user(current_user, user_id):
    try:
        data = request.get_json()
        if not data:
            raise ValidationError("No update data provided")

        # Only allow updating name and organization
        updates = {}
        if 'name' in data:
            updates['name'] = data['name']
        if 'organization' in data:
            updates['organization'] = data['organization']

        if not updates:
            raise ValidationError("No valid fields to update")

        user = UserService.update_user(user_id, updates)
        return jsonify(user.to_dict()), StatusCodes.OK

    except ResourceNotFoundError as e:
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': str(e)
            }
        }), StatusCodes.NOT_FOUND
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

@user_bp.route('/<uuid:user_id>', methods=['DELETE'])
@require_auth
def delete_user(current_user, user_id):
    try:
        UserService.delete_user(user_id)
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
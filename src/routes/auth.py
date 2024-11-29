from flask import Blueprint, request, jsonify
from src.services.auth_service import AuthService
from src.utils.exceptions import ValidationError
from src.config.constants import StatusCodes, Messages

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data or 'code' not in data:
            raise ValidationError("Missing required fields")

        user, token = AuthService.verify_google_token(data['code'])
        if not token:
            return jsonify({
                'error': {
                    'code': 'INVALID_GRANT',
                    'message': 'Invalid authorization code'
                }
            }), StatusCodes.BAD_REQUEST

        return jsonify({
            'user': user,
            'access_token': token,
            'token_type': 'Bearer',
            'expires_in': 3600  # 1 hour
        }), StatusCodes.OK

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
                'message': f"Messages.SERVER_ERROR: {str(e)}"
            }
        }), StatusCodes.INTERNAL_ERROR
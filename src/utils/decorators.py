from functools import wraps
from flask import request, jsonify
from src.services.auth_service import AuthService
from src.utils.exceptions import AuthenticationError
from src.config.constants import StatusCodes, Messages

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': Messages.INVALID_TOKEN
                }
            }), StatusCodes.UNAUTHORIZED

        try:
            parts = auth_header.split()
            if parts[0].lower() != 'bearer' or len(parts) != 2:
                raise AuthenticationError("Invalid authorization header format")
            token = parts[1]

            current_user = AuthService.verify_jwt(token)
            if not current_user:
                raise AuthenticationError(Messages.INVALID_TOKEN)

            return f(current_user=current_user, *args, **kwargs)

        except AuthenticationError as e:
            return jsonify({
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': str(e)
                }
            }), StatusCodes.UNAUTHORIZED
        except Exception as e:
            return jsonify({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': Messages.SERVER_ERROR
                }
            }), StatusCodes.INTERNAL_ERROR

    return decorated

def rate_limit(limit_key='default'):
    """
    Rate limiting decorator - placeholder for actual rate limiting implementation
    In production, you would want to use Redis or a similar solution
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # TODO: Implement actual rate limiting
            # For now, just pass through
            return f(*args, **kwargs)
        return decorated_function
    return decorator
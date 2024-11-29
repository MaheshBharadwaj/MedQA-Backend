from flask import Blueprint, request, jsonify
from src.services.auth_service import AuthService
from src.utils.exceptions import ValidationError
from src.config.constants import StatusCodes, Messages
from src.utils.decorators import require_auth
from src.services.llm_service import RAGService

llm_bp = Blueprint('llm', __name__, url_prefix='/llm')
rag_service = RAGService()

@llm_bp.route('/rag', methods=['POST'])
@require_auth
def get_rag_response(current_user):
    try:
        data = request.get_json()
        if not data or 'messages' not in data:
            raise ValidationError("Missing required fields")
        
        messages = data.get('messages', [])
        resp = rag_service.get_completion(messages)
        return jsonify({
            'response': resp
        }), StatusCodes.OK
    except ValidationError as e:
        return jsonify({
            'error': {
                'code': 'INVALID_REQUEST',
                'message': str(e)
            }
        }), StatusCodes.BAD_REQUEST


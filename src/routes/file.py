from flask import Blueprint, request, jsonify
from src.services.file_service import FileService
from src.utils.decorators import require_auth
from src.utils.exceptions import ValidationError
from src.config.constants import StatusCodes, Messages, MAX_CONTENT_LENGTH, ALLOWED_EXTENSIONS

file_bp = Blueprint('files', __name__, url_prefix='/files')
file_service = FileService()

@file_bp.route('', methods=['POST'])
@require_auth
def upload_file(current_user):
    try:
        if 'file' not in request.files:
            raise ValidationError("No file provided")

        file = request.files['file']
        if not file.filename:
            raise ValidationError("No file selected")

        # Check file size
        if request.content_length > MAX_CONTENT_LENGTH:
            raise ValidationError(Messages.FILE_TOO_LARGE)

        # Optional chat_id
        chat_id = request.form.get('chat_id')

        file_record = file_service.upload_file(
            file_obj=file,
            user_id=current_user.user_id,
            chat_id=chat_id
        )

        return jsonify({
            'file_id': str(file_record.file_id),
            'file_name': file_record.file_name,
            'file_type': file_record.file_type,
            'file_size': file_record.file_size,
            'uploaded_at': file_record.uploaded_at.isoformat()
        }), StatusCodes.OK

    except ValidationError as e:
        return jsonify({
            'error': {
                'code': 'INVALID_FILE',
                'message': str(e),
                'details': {
                    'supported_types': list(ALLOWED_EXTENSIONS)
                }
            }
        }), StatusCodes.BAD_REQUEST
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': Messages.SERVER_ERROR
            }
        }), StatusCodes.INTERNAL_ERROR

@file_bp.route('/<uuid:file_id>', methods=['GET'])
@require_auth
def get_file(current_user, file_id):
    try:
        url = file_service.get_file_url(file_id, current_user.user_id)
        return jsonify({'url': url}), StatusCodes.OK

    except ValidationError as e:
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

@file_bp.route('/<uuid:file_id>', methods=['DELETE'])
@require_auth
def delete_file(current_user, file_id):
    try:
        file_service.delete_file(file_id, current_user.user_id)
        return '', StatusCodes.OK

    except ValidationError as e:
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
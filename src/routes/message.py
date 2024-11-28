# from flask import Blueprint, request, jsonify
# from src.services.chat_service import ChatService
# from src.services.llm_service import LLMService
# from src.services.file_service import FileService
# from src.utils.decorators import require_auth
# from src.utils.exceptions import ValidationError, ResourceNotFoundError
# from src.config.constants import StatusCodes, Messages

# message_bp = Blueprint('messages', __name__)
# file_service = FileService()

# @message_bp.route('/chats/<uuid:chat_id>/messages', methods=['POST'])
# @require_auth
# def send_message(current_user, chat_id):
#     try:
#         data = request.get_json()
#         if not data or 'content' not in data or 'role' not in data:
#             raise ValidationError("Missing required fields")

#         # First verify chat access
#         chat = ChatService.get_chat(chat_id, current_user.user_id)

#         # Handle file attachments if any
#         files = []
#         if 'file_ids' in data and data['file_ids']:
#             for file_id in data['file_ids']:
#                 # Verify file access and get file records
#                 try:
#                     file_url = file_service.get_file_url(file_id, current_user.user_id)
#                     files.append(file_url)
#                 except Exception:
#                     continue

#         # If it's a user message, get LLM response
#         message = ChatService.add_message(
#             chat_id=chat_id,
#             content=data['content'],
#             role=data['role'],
#             files=files
#         )

#         if data['role'] == 'user':
#         return jsonify({
#             'error': {
#                 'code': 'INVALID_REQUEST',
#                 'message': str(e)
#             }
#         }), StatusCodes.BAD_REQUEST
#     except ResourceNotFoundError as e:
#         return jsonify({
#             'error': {
#                 'code': 'NOT_FOUND',
#                 'message': str(e)
#             }
#         }), StatusCodes.NOT_FOUND
#     except Exception as e:
#         return jsonify({
#             'error': {
#                 'code': 'INTERNAL_ERROR',
#                 'message': Messages.SERVER_ERROR
#             }
#         }), StatusCodes.INTERNAL_ERROR

# @message_bp.route('/chats/<uuid:chat_id>/messages', methods=['GET'])
# @require_auth
# def get_messages(current_user, chat_id):
#     try:
#         # Verify chat access
#         ChatService.get_chat(chat_id, current_user.user_id)

#         limit = int(request.args.get('limit', 50))
#         before = request.args.get('before')
#         include_files = request.args.get('include_files', 'false').lower() == 'true'

#         messages = ChatService.get_messages(
#             chat_id=chat_id,
#             limit=limit,
#             before=before,
#             include_files=include_files
#         )

#         return jsonify(messages), StatusCodes.OK

#     except ResourceNotFoundError as e:
#         return jsonify({
#             'error': {
#                 'code': 'NOT_FOUND',
#                 'message': str(e)
#             }
#         }), StatusCodes.NOT_FOUND
#     except Exception as e:
#         return jsonify({
#             'error': {
#                 'code': 'INTERNAL_ERROR',
#                 'message': Messages.SERVER_ERROR
#             }
#         }), StatusCodes.INTERNAL_ERROR
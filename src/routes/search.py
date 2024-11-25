from flask import Blueprint, request, jsonify
from src.models.message import Message
from src.models.chat import Chat
from src.utils.decorators import require_auth
from src.utils.exceptions import ValidationError
from src.config.constants import StatusCodes, Messages
from sqlalchemy import or_, and_, func
from datetime import datetime

search_bp = Blueprint('search', __name__, url_prefix='/search')

@search_bp.route('/messages', methods=['GET'])
@require_auth
def search_messages(current_user):
    try:
        # Required parameter
        query = request.args.get('query')
        if not query:
            raise ValidationError("Search query is required")

        # Optional parameters
        chat_id = request.args.get('chat_id')
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))

        # Base query: only search user's chats
        base_query = Message.query.join(Chat).filter(Chat.user_id == current_user.user_id)

        # Apply filters
        filters = []

        # Text search filter
        filters.append(Message.content.ilike(f'%{query}%'))

        # Chat filter if specified
        if chat_id:
            filters.append(Message.chat_id == chat_id)

        # Date range filters
        if from_date:
            try:
                from_datetime = datetime.fromisoformat(from_date)
                filters.append(Message.timestamp >= from_datetime)
            except ValueError:
                raise ValidationError("Invalid from_date format. Use ISO8601 format.")

        if to_date:
            try:
                to_datetime = datetime.fromisoformat(to_date)
                filters.append(Message.timestamp <= to_datetime)
            except ValueError:
                raise ValidationError("Invalid to_date format. Use ISO8601 format.")

        # Apply all filters
        search_query = base_query.filter(and_(*filters))

        # Get total count
        total = search_query.count()

        # Get paginated results
        messages = search_query.order_by(Message.timestamp.desc()) \
            .offset(offset) \
            .limit(limit) \
            .all()

        # Prepare results with highlighted content
        results = []
        for message in messages:
            # Simple highlight implementation
            # In a production environment, you might want to use a more sophisticated
            # text search engine like Elasticsearch
            content = message.content
            highlighted_content = content.replace(
                query,
                f'<em>{query}</em>',
                flags=2  # case-insensitive
            )

            results.append({
                'message_id': str(message.message_id),
                'chat_id': str(message.chat_id),
                'content': content,
                'timestamp': message.timestamp.isoformat(),
                'highlight': {
                    'content': [highlighted_content]
                }
            })

        return jsonify({
            'results': results,
            'total': total,
            'has_more': total > (offset + limit)
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
                'message': Messages.SERVER_ERROR
            }
        }), StatusCodes.INTERNAL_ERROR
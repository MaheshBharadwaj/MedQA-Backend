from flask import Flask, jsonify
from flask_migrate import Migrate
from src.config.constants import (
    DATABASE_URL,
    FLASK_ENV,
    MAX_CONTENT_LENGTH
)
from src.utils.db import db, migrate
from src.utils.exceptions import APIException

# Import routes
from src.routes.auth import auth_bp
from src.routes.chat import chat_bp
from src.routes.message import message_bp
from src.routes.file import file_bp
from src.routes.search import search_bp

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL  # Fixed this line
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
    app.config['ENV'] = FLASK_ENV

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)  # Added this line

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/v1/auth')
    app.register_blueprint(chat_bp, url_prefix='/v1/chats')
    app.register_blueprint(message_bp, url_prefix='/v1')  # Messages are under /chats/{chat_id}/messages
    app.register_blueprint(file_bp, url_prefix='/v1/files')
    app.register_blueprint(search_bp, url_prefix='/v1/search')

    # Error handlers
    @app.errorhandler(APIException)
    def handle_api_exception(error):
        response = {
            'error': {
                'code': error.code,
                'message': str(error)
            }
        }
        return jsonify(response), error.status_code

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': 'The requested resource was not found'
            }
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'error': {
                'code': 'METHOD_NOT_ALLOWED',
                'message': 'The method is not allowed for the requested URL'
            }
        }), 405

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An internal server error occurred'
            }
        }), 500

    # Add CORS headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    return app

app = create_app()
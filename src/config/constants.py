import os
from dotenv import load_dotenv

load_dotenv(override=True)

FLASK_APP = os.getenv('FLASK_APP', 'src.app')
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', '1') == '1'
PORT = int(os.getenv('PORT', 5000))

DATABASE_URL = os.getenv('DATABASE_URL')

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 16MB max file size
CHROMA_DB_PATH = './chroma_db'

class ModelProvider:
    ANTHROPIC = "claude"
    OPENAI = "gpt"

    @classmethod
    def list(cls):
        return [cls.ANTHROPIC, cls.OPENAI]

class Messages:
    INVALID_TOKEN = "Invalid or expired token"
    UNAUTHORIZED = "Unauthorized access"
    FILE_TOO_LARGE = "File size exceeds maximum limit"
    INVALID_FILE_TYPE = "Invalid file type"
    SERVER_ERROR = "Internal server error"

class StatusCodes:
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_ERROR = 500

RATE_LIMIT = {
    'default': '100 per hour',
    'auth': '20 per minute',
    'file_upload': '50 per hour'
}
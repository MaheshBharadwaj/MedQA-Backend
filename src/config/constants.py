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
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", '/Users/rohithvutukuru/Desktop/Fall 2024/MED 277/Project/MedQA-Backend/chroma_db')

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


PROMPT_TEMPLATE_NEW = """You are an assistant for medical question-answering tasks. Use the following pieces of retrieved context to answer the question. Read the question with atmost care and follow the instructions given. Use three sentences maximum and keep the answer concise. And include the terms in the context while reasoning.

QUESTION: {question} 

CONTEXT: {context} 

INSTRUCTIONS: {instructions}

ANSWER:"""

"""You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.

Question: {question} 

Context: {context} 

Answer:"""

SYSTEM_PROMPT_TEMPLATE_CHAT_HISTORY = """1. You are an assistant for medical question-answering tasks. You are given retrieved CONTEXT and INSTRUCTIONS in this System message, and the chat history attached. Use the following pieces of retrieved CONTEXT to answer the question in the chat and follow the INSTRUCTIONS given. Use three sentences maximum and keep the answer concise and include the terms in the context while reasoning.

CONTEXT: {context} 

INSTRUCTIONS: {instructions}

"""

COMMON_INSTRUCTIONS = """1. You are a highly knowledgeable medical assistant specializing in advising on surgical procedures. Your primary role is to help both doctors and patients decide whether a given surgery is appropriate be conducted as an inpatient or outpatient procedure,based on the context given. You provide detailed explanations to support your recommendations, ensuring that users make informed decisions.
        2. You can save huge costs if you can correctly identify the case of Outpatient Surgery, so please keep this in mind. Suggest inpatient surgery only if the given context suggests that the patients are not suitable for outpatient surgery.
        3. If the patients are healthy currently and comorbidities are well controlled or have medical clearence, it is a good sign for Outpatient surgery.
        4. If you do not know the answer from the context you have, Please convey to user that you are not sure.
        5. If the question is not in your domain, please remind user about your expertise."""
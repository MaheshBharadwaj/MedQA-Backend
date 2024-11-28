from google.oauth2 import id_token
from google.auth.transport import requests
import jwt as pyjwt  # Changed import
from datetime import datetime, timedelta
from src.config.constants import GOOGLE_CLIENT_ID, JWT_SECRET_KEY
from src.models.user import User
from src.utils.db import db

class AuthService:
    @staticmethod
    def verify_google_token(token):
        try:
            # Verify the token with Google
            idinfo = id_token.verify_oauth2_token(
                token, requests.Request(), GOOGLE_CLIENT_ID)

            # Get user info from token
            email = idinfo['email']
            name = idinfo.get('name', '')

            # Find or create user
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(email=email, name=name)
                db.session.add(user)
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()

            # Generate JWT token
            return user.to_dict(), AuthService.generate_jwt(user)

        except ValueError:
            # Invalid token
            return None

    @staticmethod
    def generate_jwt(user):
        payload = {
            'user_id': str(user.user_id),
            'email': user.email,
            'exp': datetime.utcnow() + timedelta(days=1)
        }
        return pyjwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')  # Changed to pyjwt

    @staticmethod
    def verify_jwt(token):
        try:
            payload = pyjwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])  # Changed to pyjwt
            return User.query.filter_by(user_id=payload['user_id']).first()
        except pyjwt.ExpiredSignatureError:
            return None
        except pyjwt.InvalidTokenError:
            return None
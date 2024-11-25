from src.models.user import User
from src.utils.db import db
from src.utils.exceptions import ResourceNotFoundError

class UserService:
    @staticmethod
    def get_user_by_id(user_id):
        user = User.query.get(user_id)
        if not user:
            raise ResourceNotFoundError("User not found")
        return user

    @staticmethod
    def get_user_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def create_user(email, name, organization=None):
        user = User(
            email=email,
            name=name,
            organization=organization
        )
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def update_user(user_id, updates):
        user = UserService.get_user_by_id(user_id)
        
        if 'name' in updates:
            user.name = updates['name']
        if 'organization' in updates:
            user.organization = updates['organization']
        
        db.session.commit()
        return user

    @staticmethod
    def delete_user(user_id):
        user = UserService.get_user_by_id(user_id)
        db.session.delete(user)
        db.session.commit()
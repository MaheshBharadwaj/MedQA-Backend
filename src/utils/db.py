from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    """Initialize the database with the Flask app"""
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models here to ensure they're known to Flask-Migrate
    from src.models.user import User
    from src.models.chat import Chat
    from src.models.message import Message
    from src.models.file import File

    with app.app_context():
        db.create_all()

def commit_changes():
    """Commit changes to database with error handling"""
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

def add_to_db(model):
    """Add a model instance to database"""
    try:
        db.session.add(model)
        commit_changes()
    except Exception as e:
        db.session.rollback()
        raise e
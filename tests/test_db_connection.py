import os
import sys
from sqlalchemy import text

# Ensure project root is on the Python path so that the DB package can be imported
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from DB.database import engine, SessionLocal
from DB.models import User, UserSettings, ThemeType
from DB.base import Base


def setup_module(module):
    """Create all database tables before tests run."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    if "sqlite" in str(engine.url):
        with engine.begin() as conn:
            conn.execute(text("PRAGMA foreign_keys = ON"))


def teardown_module(module):
    """Drop all tables after tests complete."""
    Base.metadata.drop_all(bind=engine)


def test_database_connection():
    """Verify that a basic database connection works."""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar()
    assert result == 1


def test_user_creation_and_cleanup():
    """Ensure a user and related settings can be created and removed."""
    db = SessionLocal()
    try:
        user = User(
            username="test_user",
            email="test@example.com",
            password_hash="test_hash",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        assert user.user_id is not None

        settings = UserSettings(
            user_id=user.user_id,
            theme=ThemeType.LIGHT,
            preferred_model="Llama",
            language_preference="English",
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
        # refresh user instance so relationship can be loaded
        db.refresh(user)
        assert settings.setting_id is not None

        retrieved = db.query(User).filter(User.username == "test_user").first()
        assert retrieved is not None
        assert retrieved.settings is not None
        assert retrieved.settings.theme == ThemeType.LIGHT

        settings_id = settings.setting_id
        user_id = user.user_id
        db.delete(settings)
        db.delete(user)
        db.commit()
    finally:
        db.close()

    with SessionLocal() as check_db:
        assert (
            check_db.query(User).filter(User.username == "test_user").first()
            is None
        )
        assert (
            check_db.query(UserSettings)
            .filter(UserSettings.setting_id == settings_id)
            .first()
            is None
        )
        assert (
            check_db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
            is None
        )

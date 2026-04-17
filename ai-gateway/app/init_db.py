"""Database initialization script."""
import secrets
from app.database import engine, SessionLocal, Base
from app.models import User


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")


def create_test_user():
    """Create a test user for development."""
    db = SessionLocal()
    try:
        # Check if test user exists
        existing = db.query(User).filter(User.username == "test_user").first()
        if existing:
            print(f"Test user already exists. API Key: {existing.api_key}")
            return existing.api_key

        # Create test user
        api_key = f"sk-test-{secrets.token_urlsafe(32)}"
        user = User(
            username="test_user",
            api_key=api_key,
            monthly_token_quota=10000000,  # 10M tokens
            is_active=1
        )
        db.add(user)
        db.commit()
        print(f"Test user created. API Key: {api_key}")
        return api_key
    finally:
        db.close()


def reset_db():
    """Drop and recreate all tables."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database reset complete.")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "reset":
        reset_db()
    else:
        init_db()
        create_test_user()

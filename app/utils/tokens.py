import secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy import select


def generate_verification_token():
    """Generate a secure random token"""
    return secrets.token_urlsafe(32)

def create_verification_token(user, db):
    """Create and assign verification token to user"""
    user.verification_token = generate_verification_token()
    user.token_expiry = datetime.now(timezone.utc) + timedelta(hours=24)
    db.session.commit()
    return user.verification_token


def validate_verification_token(token, User, db):
    """Validate token and return user if valid"""
    stmt = select(User).where(User.verification_token == token)
    user = db.session.execute(stmt).scalar_one_or_none()

    if not user:
        return None, "Invalid verification token"

    if not user.token_expiry or datetime.now(timezone.utc) > user.token_expiry:
        return None, "Verification token has expired"

    return user, None


def verify_user(user, db):
    """Mark user as verified and clear token"""
    user.is_verified = True
    user.verification_token = None
    user.token_expiry = None
    user.verification_date = datetime.now(timezone.utc)
    db.session.commit()


def get_user_by_email(email, User, db):
    """Get user by email"""
    stmt = select(User).where(User.email == email)
    return db.session.execute(stmt).scalar_one_or_none()


def get_user_by_id(user_id, User, db):
    """Get user by ID"""
    stmt = select(User).where(User.id == user_id)
    return db.session.execute(stmt).scalar_one_or_none()
from sqlalchemy import select


def get_user_by_email(email, User, db):
    """Get user by email"""
    stmt = select(User).where(User.email == email)
    return db.session.execute(stmt).scalar_one_or_none()


def get_user_by_id(user_id, User, db):
    """Get user by ID"""
    stmt = select(User).where(User.id == user_id)
    return db.session.execute(stmt).scalar_one_or_none()
from fastapi import HTTPException
from sqlalchemy.orm import Session

from auth.auth import bcrypt_hash, create_access_token, create_refresh_token
from models.models import User


def get_user_by_email(session: Session, email: str) -> User | None:
    return session.query(User).filter(User.email == email).first()


def create_user(session: Session, name: str, email: str, password: str) -> User:
    existing_user = get_user_by_email(session, email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=name,
        email=email,
        password=bcrypt_hash.hash(password),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


def authenticate_user(session: Session, email: str, password: str) -> dict:
    user = get_user_by_email(session, email)
    if not user or not bcrypt_hash.verify(password, user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    return {
        "access_token": create_access_token({"sub": user.email}),
        "refresh_token": create_refresh_token({"sub": user.email}),
    }

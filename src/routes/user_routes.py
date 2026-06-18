from schemas.user_schema import UserCreateRequest, UserResponse
from models.models import User
from fastapi import APIRouter, HTTPException, Request, status,Depends
from sqlalchemy.orm import Session
from dependencies.dependencies import get_session
from auth.auth import bcrypt_hash

user_router = APIRouter(prefix="", tags=["user"])


@user_router.post("/users", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_user(user_request: UserCreateRequest, session: Session = Depends(get_session)):
    existing_user = session.query(User).filter(User.email == user_request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hash_password = bcrypt_hash.hash(user_request.password)
    new_user = User(
        name=user_request.name,
        email=user_request.email,
        password=hash_password
    )

    session.add(new_user)
    session.commit()

    return UserResponse(
        name=new_user.name,
        email=new_user.email
    )
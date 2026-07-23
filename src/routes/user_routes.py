from auth.acess import get_current_user, refresh_user
from schemas.shortener_schema import shortenerRequest, shortenerResponse
from schemas.token_schema import TokenResponse, RefreshTokenResponse,RefreshTokenRequest
from schemas.user_schema import UserCreateRequest, UserLoginRequest, UserResponse
from models.models import User
from fastapi import APIRouter, Request, status,Depends
from sqlalchemy.orm import Session
from dependencies.dependencies import get_session
from services.short_url_service import create_short_url
from services.user_service import authenticate_user, create_user as create_user_service
from core.rate_limiter import limiter
user_router = APIRouter(prefix="/user", tags=["user"])


@user_router.post("/create", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
@limiter.limit("5/minute")
async def create_user(request: Request, user_request: UserCreateRequest, session: Session = Depends(get_session)):
    new_user = create_user_service(session, user_request.name, user_request.email, user_request.password)

    return UserResponse(
        name=new_user.name,
        email=new_user.email
    )


@user_router.post("/login", status_code=status.HTTP_200_OK, response_model=TokenResponse)
@limiter.limit("5/minute")
async def login_user(request: Request,user_request: UserLoginRequest, session: Session = Depends(get_session)):
    tokens = authenticate_user(session, user_request.email, user_request.password)

    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"]
    )

@user_router.get("/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
@limiter.limit("50/minute")
async def get_current_user_info(request: Request, current_user: User = Depends(get_current_user)):
    return UserResponse(
        name=current_user.name,
        email=current_user.email
    )

@user_router.post("/createUrl", status_code=status.HTTP_201_CREATED, response_model=shortenerResponse)
@limiter.limit("5/minute")
async def create_url(request: Request, shortener_request: shortenerRequest, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    short_url = create_short_url(session, shortener_request.url, current_user.id)
    base_url = str(request.base_url).rstrip("/")

    return {
        "url": shortener_request.url,
        "short_url": f"{base_url}/{short_url.hash_url}",
    }

@user_router.post("/refresh", status_code=status.HTTP_200_OK, response_model=TokenResponse)
@limiter.limit("5/minute")
async def refresh_token(RefreshTokenRequest: RefreshTokenRequest, request: Request, session: Session = Depends(get_session)):
    paylaod = refresh_user(RefreshTokenRequest.access_token)


    return RefreshTokenResponse( refresh_token=paylaod["access_token"], token_type="bearer")



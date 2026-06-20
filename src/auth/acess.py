from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
import jwt

from auth.auth import oauth2_scheme, decode_token
from dependencies.dependencies import get_session
from models.models import User
from services.user_service import get_user_by_email


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> User:
    """
    Dependency que extrai o usuário atual a partir do token Bearer.
    Uso: current_user: User = Depends(get_current_user)
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)

        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido. Use um access token.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_email: str = payload.get("sub")
        if user_email is None:
            raise credentials_exception

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise credentials_exception

    user = get_user_by_email(session, user_email)
    if user is None:
        raise credentials_exception

    return user

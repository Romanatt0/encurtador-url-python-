
import secrets
import string

from fastapi import APIRouter, HTTPException, Request, status,Depends
from urllib.parse import urlparse
from sqlalchemy.orm import Session
from dependencies.dependencies import get_session
from models.models import ShortUrl
from schemas.shortener_schema import shortenerRequest, shortenerResponse

shortener_router = APIRouter(prefix="", tags=["users"])

ALPHABET = string.ascii_letters + string.digits
SHORT_ID_LENGTH = 7


def generate_short_id(length: int = SHORT_ID_LENGTH) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))

def validate_url(url: str) -> bool:
    try:
        result = urlparse(url)
        if not result.scheme or not result.netloc:
            return False
    except ValueError:
        return False

    return True


@shortener_router.post("/short", status_code=status.HTTP_201_CREATED, response_model=shortenerResponse)
async def shortenerUrl(request: Request, shortener_request: shortenerRequest, session: Session = Depends(get_session)):

    if validate_url(shortener_request.url) != True:
        raise HTTPException(status_code=400, detail="URL invalid")
    
    url = session.query(ShortUrl).filter(ShortUrl.origin_url == shortener_request.url).first()
        
    if url:
        raise HTTPException(status_code=400, detail="URL already exists")
    
    try:
        short_id = generate_short_id()
        base_url = str(request.base_url).rstrip("/")

        new_url = ShortUrl(
            origin_url=shortener_request.url,
            hash_url=short_id
        )

        session.add(new_url)
        session.commit()
        

        return {
            "url": shortener_request.url,
            "short_url": f"{base_url}/{short_id}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

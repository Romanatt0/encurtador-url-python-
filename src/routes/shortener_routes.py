
import secrets
import string
from datetime import date

from fastapi import APIRouter, HTTPException, Request, status,Depends
from fastapi.responses import RedirectResponse, StreamingResponse
from urllib.parse import urlparse
from sqlalchemy.orm import Session
from dependencies.dependencies import get_session
from models.models import ShortUrl, UrlMetric
from schemas.shortener_schema import shortenerRequest, shortenerResponse
import qrcode
import io
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

shortener_router = APIRouter(prefix="", tags=["url_shortener"])

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
    
@shortener_router.get("/{short_id}")
@limiter.limit("5/minute")
async def redirect_to_url(request: Request, short_id: str, session: Session = Depends(get_session)):
    short_url = session.query(ShortUrl).filter_by(hash_url=short_id).first()

    if not short_url:
        raise HTTPException(status_code=404, detail="URL not found")

    today = date.today()
    metric = (
        session.query(UrlMetric)
        .filter_by(
            short_url_id=short_url.id,
            day=today.day,
            month=today.month,
            year=today.year,
        )
        .first()
    )

    if metric:
        metric.amount += 1
    else:
        metric = UrlMetric(
            day=today.day,
            month=today.month,
            year=today.year,
            amount=1,
            short_url_id=short_url.id,
        )
        session.add(metric)

    session.commit()

    return RedirectResponse(url=short_url.origin_url)

@shortener_router.get("/{short_id}/qrcode")
async def generate_qrcode(request: Request, short_id: str, session: Session = Depends(get_session)):
    short_url = session.query(ShortUrl).filter_by(hash_url=short_id).first()
    
    if not short_url:
        raise HTTPException(status_code=404, detail="URL not found")

    base_url = str(request.base_url).rstrip("/")
    redirect_url = f"{base_url}/{short_id}"

    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(redirect_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="image/png")

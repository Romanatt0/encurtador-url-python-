from fastapi import APIRouter, HTTPException, Request, status,Depends
from fastapi.responses import RedirectResponse, StreamingResponse
from sqlalchemy.orm import Session
from auth.acess import get_current_user, get_optional_current_user
from dependencies.dependencies import get_session
from models.models import User
from schemas.shortener_schema import shortenerRequest, shortenerResponse, allLinksResponse
import qrcode
import io
from core.rate_limiter import limiter
from services.short_url_service import create_short_url, get_active_short_url_or_404, get_all_short_urls, register_url_access

shortener_router = APIRouter(prefix="", tags=["url_shortener"])


@shortener_router.post("/short", status_code=status.HTTP_201_CREATED, response_model=shortenerResponse)
@limiter.limit("10/minute")
async def shortenerUrl(request: Request, shortener_request: shortenerRequest, current_user: User | None = Depends(get_optional_current_user), session: Session = Depends(get_session)):
    try:

        if current_user:
            short_url = create_short_url(session, shortener_request.url, current_user.id)  
        else:
            short_url = create_short_url(session, shortener_request.url)

        base_url = str(request.base_url).rstrip("/")

        return {
            "url": shortener_request.url,
            "short_url": f"{base_url}/{short_url.hash_url}",
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="Error occurred while creating short URL")

    
@shortener_router.get("/s/{short_id}")
@limiter.limit("5/minute")
async def redirect_to_url(request: Request, short_id: str, session: Session = Depends(get_session)):
    short_url = get_active_short_url_or_404(session, short_id)
    register_url_access(session, short_url)

    return RedirectResponse(url=short_url.origin_url)

@shortener_router.get("/{short_id}/qrcode")
@limiter.limit("5/minute")
async def generate_qrcode(request: Request, short_id: str, session: Session = Depends(get_session)):
    short_url = get_active_short_url_or_404(session, short_id)

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


@shortener_router.get("/all_links", status_code=status.HTTP_200_OK, response_model=allLinksResponse)
@limiter.limit("10/minute")
async def get_all_links(request: Request, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):

    try:
        short_urls = get_all_short_urls(session, current_user)
        base_url = str(request.base_url).rstrip("/")

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))
    
    return allLinksResponse(
        links=[
            shortenerResponse(
                url=short_url.origin_url,
                short_url=f"{base_url}/{short_url.hash_url}",
                expiration_date=short_url.expires_at.isoformat() if short_url.expires_at else None
            )
            for short_url in short_urls
        ]
    )
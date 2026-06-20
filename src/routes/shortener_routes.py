from fastapi import APIRouter, HTTPException, Request, status,Depends
from fastapi.responses import RedirectResponse, StreamingResponse
from sqlalchemy.orm import Session
from dependencies.dependencies import get_session
from schemas.shortener_schema import shortenerRequest, shortenerResponse
import qrcode
import io
from core.rate_limiter import limiter
from services.short_url_service import create_short_url, get_active_short_url_or_404, register_url_access

shortener_router = APIRouter(prefix="", tags=["url_shortener"])


@shortener_router.post("/short", status_code=status.HTTP_201_CREATED, response_model=shortenerResponse)
async def shortenerUrl(request: Request, shortener_request: shortenerRequest, session: Session = Depends(get_session)):
    try:
        short_url = create_short_url(session, shortener_request.url)
        base_url = str(request.base_url).rstrip("/")

        return {
            "url": shortener_request.url,
            "short_url": f"{base_url}/{short_url.hash_url}",
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))
    
@shortener_router.get("/{short_id}")
@limiter.limit("5/minute")
async def redirect_to_url(request: Request, short_id: str, session: Session = Depends(get_session)):
    short_url = get_active_short_url_or_404(session, short_id)
    register_url_access(session, short_url)

    return RedirectResponse(url=short_url.origin_url)

@shortener_router.get("/{short_id}/qrcode")
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

from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.models import ShortUrl, UrlMetric
from utils.short_code import generate_short_id
from utils.url_utils import validate_url

ANONYMOUS_EXPIRATION_DAYS = 7
AUTHENTICATED_EXPIRATION_DAYS = 30


def _build_expiration(user_id: int | None) -> datetime:
    days = AUTHENTICATED_EXPIRATION_DAYS if user_id is not None else ANONYMOUS_EXPIRATION_DAYS
    return datetime.utcnow() + timedelta(days=days)


def _normalize_datetime(value: datetime) -> datetime:
    if value.tzinfo is not None:
        return value.replace(tzinfo=None)
    return value


def create_short_url(session: Session, original_url: str, user_id: int | None = None) -> ShortUrl:
    if not validate_url(original_url):
        raise HTTPException(status_code=400, detail="URL invalid")

    short_id = generate_short_id()
    while session.query(ShortUrl).filter(ShortUrl.hash_url == short_id).first():
        short_id = generate_short_id()

    short_url = ShortUrl(
        origin_url=original_url,
        hash_url=short_id,
        user_id=user_id,
        expires_at=_build_expiration(user_id),
    )

    session.add(short_url)
    session.commit()
    session.refresh(short_url)

    return short_url


def get_short_url_by_hash(session: Session, short_id: str) -> ShortUrl | None:
    return session.query(ShortUrl).filter(ShortUrl.hash_url == short_id).first()


def get_active_short_url_or_404(session: Session, short_id: str) -> ShortUrl:
    short_url = get_short_url_by_hash(session, short_id)
    if not short_url:
        raise HTTPException(status_code=404, detail="URL not found")

    if short_url.expires_at and _normalize_datetime(short_url.expires_at) <= datetime.utcnow():
        raise HTTPException(status_code=410, detail="URL expired")

    return short_url


def register_url_access(session: Session, short_url: ShortUrl) -> None:
    today = datetime.utcnow().date()
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

from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.models import UrlMetric, User
from services.short_url_service import get_short_url_by_hash


def _get_owned_short_url_or_404(session: Session, short_id: str, current_user: User):
    short_url = get_short_url_by_hash(session, short_id)
    if not short_url:
        raise HTTPException(status_code=404, detail="Short URL not found")

    if short_url.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Metrics are only available for registered users URLs",
        )

    if short_url.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access metrics for this URL",
        )

    return short_url


def get_daily_metrics(session: Session, short_id: str, current_user: User) -> UrlMetric:
    short_url = _get_owned_short_url_or_404(session, short_id, current_user)
    today = date.today()

    metric = session.query(UrlMetric).filter(
        UrlMetric.short_url_id == short_url.id,
        UrlMetric.day == today.day,
        UrlMetric.month == today.month,
        UrlMetric.year == today.year,
    ).first()

    if not metric:
        raise HTTPException(status_code=404, detail="Metrics not found")

    return metric


def get_monthly_metrics(session: Session, short_id: str, current_user: User) -> dict:
    short_url = _get_owned_short_url_or_404(session, short_id, current_user)
    today = date.today()

    metrics = session.query(UrlMetric).filter(
        UrlMetric.short_url_id == short_url.id,
        UrlMetric.month == today.month,
        UrlMetric.year == today.year,
    ).all()

    if not metrics:
        raise HTTPException(status_code=404, detail="Metrics not found")

    return {
        "month": today.month,
        "year": today.year,
        "amount": sum(metric.amount for metric in metrics),
    }


def get_yearly_metrics(session: Session, short_id: str, current_user: User) -> dict:
    short_url = _get_owned_short_url_or_404(session, short_id, current_user)
    current_year = date.today().year

    metrics = session.query(UrlMetric).filter(
        UrlMetric.short_url_id == short_url.id,
        UrlMetric.year == current_year,
    ).all()

    if not metrics:
        raise HTTPException(status_code=404, detail="Metrics not found")

    return {
        "year": current_year,
        "amount": sum(metric.amount for metric in metrics),
    }

from models.models import ShortUrl, UrlMetric
from dependencies.dependencies import get_session
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from schemas.metric_schema import urlMetricDayResponse, urlMetricMonthResponse, urlMetricRequest, urlMetricYearResponse
from datetime import date


metrics_router = APIRouter(prefix="", tags=["url_metrics"])


@metrics_router.get("/metrics/day/{short_id}", response_model=urlMetricDayResponse)
async def get_metrics(short_id: str, session: Session = Depends(get_session)):
    url = session.query(ShortUrl).filter(ShortUrl.hash_url == short_id).first()
    if not url:
        raise HTTPException(status_code=404, detail="Short URL not found")

    today = date.today()
    metric = session.query(UrlMetric).filter(
        UrlMetric.short_url_id == url.id,
        UrlMetric.day == today.day,
        UrlMetric.month == today.month,
        UrlMetric.year == today.year,
    ).first()

    if not metric:
        raise HTTPException(status_code=404, detail="Metrics not found")
    
    urlMetric = urlMetricDayResponse(
        day=metric.day,
        month=metric.month,
        year=metric.year,
        amount=metric.amount
        )

    
    return urlMetric

@metrics_router.get("/metrics/month/{short_id}", response_model=urlMetricMonthResponse)
async def get_metrics(short_id: str, session: Session = Depends(get_session)):
    url = session.query(ShortUrl).filter(
        ShortUrl.hash_url == short_id
    ).first()

    if not url:
        raise HTTPException(status_code=404, detail="Short URL not found")

    today = date.today()

    metrics = session.query(UrlMetric).filter(
        UrlMetric.short_url_id == url.id,
        UrlMetric.month == today.month,
        UrlMetric.year == today.year,
    ).all()

    if not metrics:
        raise HTTPException(status_code=404, detail="Metrics not found")

    metric_amount = sum(metric.amount for metric in metrics)

    return urlMetricMonthResponse(
        month=today.month,
        year=today.year,
        amount=metric_amount
    )


@metrics_router.get("/metrics/year/{short_id}", response_model=urlMetricYearResponse)
async def get_metrics_year(
    short_id: str,
    session: Session = Depends(get_session)
):
    url = session.query(ShortUrl).filter(
        ShortUrl.hash_url == short_id
    ).first()

    if not url:
        raise HTTPException(status_code=404, detail="Short URL not found")

    current_year = date.today().year

    metrics = session.query(UrlMetric).filter(
        UrlMetric.short_url_id == url.id,
        UrlMetric.year == current_year
    ).all()

    if not metrics:
        raise HTTPException(status_code=404, detail="Metrics not found")

    total_amount = sum(metric.amount for metric in metrics)

    return urlMetricYearResponse(
        year=current_year,
        amount=total_amount
    )
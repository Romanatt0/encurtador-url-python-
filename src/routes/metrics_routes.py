from auth.acess import get_current_user
from dependencies.dependencies import get_session
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Request
from schemas.metric_schema import urlMetricDayResponse, urlMetricMonthResponse, urlMetricYearResponse
from services.metric_service import get_daily_metrics, get_monthly_metrics, get_yearly_metrics
from models.models import User
from core.rate_limiter import limiter

metrics_router = APIRouter(prefix="", tags=["url_metrics"])


@metrics_router.get("/metrics/day/{short_id}", response_model=urlMetricDayResponse)
@limiter.limit("5/minute")
async def get_metrics_day(request: Request, short_id: str, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    metric = get_daily_metrics(session, short_id, current_user)
    return urlMetricDayResponse(
        day=metric.day,
        month=metric.month,
        year=metric.year,
        amount=metric.amount
    )

@metrics_router.get("/metrics/month/{short_id}", response_model=urlMetricMonthResponse)
@limiter.limit("5/minute")
async def get_metrics_month(request: Request, short_id: str, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    metrics = get_monthly_metrics(session, short_id, current_user)
    return urlMetricMonthResponse(**metrics)

@metrics_router.get("/metrics/year/{short_id}", response_model=urlMetricYearResponse)
@limiter.limit("5/minute")
async def get_metrics_year(
    request: Request,
    short_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    metrics = get_yearly_metrics(session, short_id, current_user)
    return urlMetricYearResponse(**metrics)

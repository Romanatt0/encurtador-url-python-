from auth.acess import get_current_user
from dependencies.dependencies import get_session
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from schemas.metric_schema import urlMetricDayResponse, urlMetricMonthResponse, urlMetricYearResponse
from services.metric_service import get_daily_metrics, get_monthly_metrics, get_yearly_metrics
from models.models import User

metrics_router = APIRouter(prefix="", tags=["url_metrics"])


@metrics_router.get("/metrics/day/{short_id}", response_model=urlMetricDayResponse)
async def get_metrics(short_id: str, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    metric = get_daily_metrics(session, short_id)

    urlMetric = urlMetricDayResponse(
        day=metric.day,
        month=metric.month,
        year=metric.year,
        amount=metric.amount
        )

    
    return urlMetric

@metrics_router.get("/metrics/month/{short_id}", response_model=urlMetricMonthResponse)
async def get_metrics(short_id: str, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    metrics = get_monthly_metrics(session, short_id)

    return urlMetricMonthResponse(**metrics)


@metrics_router.get("/metrics/year/{short_id}", response_model=urlMetricYearResponse)
async def get_metrics_year(
    short_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    metrics = get_yearly_metrics(session, short_id)

    return urlMetricYearResponse(**metrics)

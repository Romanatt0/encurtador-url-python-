from datetime import date

import pytest
from fastapi import HTTPException

from models.models import UrlMetric
from services.metric_service import (
    get_daily_metrics,
    get_monthly_metrics,
    get_yearly_metrics,
)


class TestGetDailyMetrics:
    def test_found(self, db_session, short_url):
        today = date.today()
        metric = UrlMetric(
            day=today.day, month=today.month, year=today.year,
            amount=5, short_url_id=short_url.id,
        )
        db_session.add(metric)
        db_session.commit()

        result = get_daily_metrics(db_session, short_url.hash_url, short_url.user)
        assert result.amount == 5

    def test_not_found_raises_404(self, db_session, short_url):
        with pytest.raises(HTTPException) as exc:
            get_daily_metrics(db_session, short_url.hash_url, short_url.user)
        assert exc.value.status_code == 404

    def test_not_owner_raises_403(self, db_session, short_url, other_user):
        today = date.today()
        metric = UrlMetric(
            day=today.day, month=today.month, year=today.year,
            amount=5, short_url_id=short_url.id,
        )
        db_session.add(metric)
        db_session.commit()

        with pytest.raises(HTTPException) as exc:
            get_daily_metrics(db_session, short_url.hash_url, other_user)
        assert exc.value.status_code == 403

    def test_anonymous_url_raises_403(self, db_session, anonymous_short_url, test_user):
        with pytest.raises(HTTPException) as exc:
            get_daily_metrics(db_session, anonymous_short_url.hash_url, test_user)
        assert exc.value.status_code == 403

    def test_nonexistent_url_raises_404(self, db_session, test_user):
        with pytest.raises(HTTPException) as exc:
            get_daily_metrics(db_session, "nonexistent", test_user)
        assert exc.value.status_code == 404


class TestGetMonthlyMetrics:
    def test_sum_multiple_days(self, db_session, short_url):
        today = date.today()
        for day_amount in [3, 7]:
            metric = UrlMetric(
                day=today.day, month=today.month, year=today.year,
                amount=day_amount, short_url_id=short_url.id,
            )
            db_session.add(metric)
        db_session.commit()

        result = get_monthly_metrics(db_session, short_url.hash_url, short_url.user)
        assert result["amount"] == 10
        assert result["month"] == today.month
        assert result["year"] == today.year

    def test_not_found_raises_404(self, db_session, short_url):
        with pytest.raises(HTTPException) as exc:
            get_monthly_metrics(db_session, short_url.hash_url, short_url.user)
        assert exc.value.status_code == 404


class TestGetYearlyMetrics:
    def test_sum_multiple_months(self, db_session, short_url):
        today = date.today()
        for month in [1, 6]:
            metric = UrlMetric(
                day=1, month=month, year=today.year,
                amount=10, short_url_id=short_url.id,
            )
            db_session.add(metric)
        db_session.commit()

        result = get_yearly_metrics(db_session, short_url.hash_url, short_url.user)
        assert result["amount"] == 20
        assert result["year"] == today.year

    def test_not_found_raises_404(self, db_session, short_url):
        with pytest.raises(HTTPException) as exc:
            get_yearly_metrics(db_session, short_url.hash_url, short_url.user)
        assert exc.value.status_code == 404

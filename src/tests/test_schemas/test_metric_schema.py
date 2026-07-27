import pytest
from pydantic import ValidationError
from schemas.metric_schema import (
    urlMetricRequest,
    urlMetricDayResponse,
    urlMetricMonthResponse,
    urlMetricYearResponse,
)


class TestUrlMetricRequest:
    def test_empty_request(self):
        data = urlMetricRequest()
        assert data.day is None
        assert data.month is None
        assert data.year is None

    def test_partial_request(self):
        data = urlMetricRequest(day=15)
        assert data.day == 15
        assert data.month is None


class TestUrlMetricDayResponse:
    def test_valid(self):
        data = urlMetricDayResponse(day=15, month=7, year=2025, amount=42)
        assert data.day == 15
        assert data.month == 7
        assert data.year == 2025
        assert data.amount == 42


class TestUrlMetricMonthResponse:
    def test_valid(self):
        data = urlMetricMonthResponse(month=7, year=2025, amount=100)
        assert data.month == 7
        assert data.year == 2025
        assert data.amount == 100


class TestUrlMetricYearResponse:
    def test_valid(self):
        data = urlMetricYearResponse(year=2025, amount=500)
        assert data.year == 2025
        assert data.amount == 500

import pytest
from pydantic import ValidationError
from schemas.shortener_schema import shortenerRequest, shortenerResponse, allLinksResponse


class TestShortenerRequest:
    def test_valid_request(self):
        data = shortenerRequest(url="https://example.com")
        assert data.url == "https://example.com"

    def test_missing_url_raises(self):
        with pytest.raises(ValidationError):
            shortenerRequest()


class TestShortenerResponse:
    def test_valid_response(self):
        data = shortenerResponse(url="https://example.com", short_url="http://localhost/s/abc1234")
        assert data.url == "https://example.com"
        assert data.short_url == "http://localhost/s/abc1234"

    def test_with_expiration(self):
        data = shortenerResponse(
            url="https://example.com",
            short_url="http://localhost/s/abc1234",
            expiration_date="2025-01-01T00:00:00",
        )
        assert data.expiration_date == "2025-01-01T00:00:00"

    def test_expiration_defaults_to_none(self):
        data = shortenerResponse(url="https://example.com", short_url="http://localhost/s/abc1234")
        assert data.expiration_date is None


class TestAllLinksResponse:
    def test_valid_response(self):
        link = shortenerResponse(url="https://example.com", short_url="http://localhost/s/abc1234")
        data = allLinksResponse(links=[link])
        assert len(data.links) == 1
        assert data.links[0].url == "https://example.com"

    def test_empty_links(self):
        data = allLinksResponse(links=[])
        assert len(data.links) == 0

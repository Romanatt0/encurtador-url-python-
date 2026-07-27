from utils.url_utils import validate_url


class TestValidateUrl:
    def test_valid_http_url(self):
        assert validate_url("http://example.com") is True

    def test_valid_https_url(self):
        assert validate_url("https://example.com") is True

    def test_valid_url_with_path(self):
        assert validate_url("https://example.com/path/to/page") is True

    def test_valid_url_with_query(self):
        assert validate_url("https://example.com/page?q=test&lang=en") is True

    def test_url_without_scheme(self):
        assert validate_url("example.com") is False

    def test_url_without_netloc(self):
        assert validate_url("https://") is False

    def test_empty_string(self):
        assert validate_url("") is False

    def test_random_text(self):
        assert validate_url("not a url") is False

    def test_valid_localhost(self):
        assert validate_url("http://localhost:8000") is True

    def test_valid_ip_address(self):
        assert validate_url("https://192.168.1.1") is True

from urllib.parse import urlparse


def validate_url(url: str) -> bool:
    try:
        result = urlparse(url)
        if not result.scheme or not result.netloc:
            return False
    except ValueError:
        return False

    return True

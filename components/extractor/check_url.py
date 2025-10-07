from re import search
from urllib.parse import urlparse, parse_qs, ParseResult

def is_youtube(url: str) -> bool:
    """
    Affirm the YouTube domain and that there is something after the domain.
    """
    return bool(search(r'^(?:http|//).*(?:youtube\.com|youtu\.be)/.+', url))

def is_video(url: str) -> bool:
    if not is_youtube(url):
        return False
    parsed_url = urlparse(url)
    if parsed_url.path in ('/watch', '/shorts/', '/embed/'):
        return True
    return parsed_url.netloc == 'youtu.be'

def is_playlist(url: str) -> bool:
    if not is_youtube(url):
        return False
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return 'list' in query_params

def is_channel(url: str) -> bool:
    if not is_youtube(url):
        return False
    parsed_url = urlparse(url)
    return parsed_url.path.startswith(('/c/', '/user/', '/channel/', '/@'))

from typing import Any, Dict, cast
from urllib.parse import urlparse, parse_qs
from urllib.request import urlopen

from bs4 import BeautifulSoup
from feedparser import parse # type: ignore

from .check_url import is_youtube, is_playlist, is_channel

def get_sub_info_from_yt_url(url: str) -> Dict[str, Any]:
    if not is_youtube(url):
        raise Exception(url+" is not a youtube URL.")
    if is_playlist(url):
        return get_feed_details(get_playlist_feed(url))
    return get_feed_details(get_channel_feed(url))

def get_playlist_feed(url: str) -> str:
    parsed_url = urlparse(url)
    # Extract playlist ID from query parameters
    query_params = parse_qs(parsed_url.query)
    playlist_id = query_params['list'][0]
    return "https://www.youtube.com/feeds/videos.xml?playlist_id="+playlist_id

def get_channel_feed(url: str, html: str = '') -> str:
    html = html or urlopen(url).read().decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    link_obj = soup.find('link', {'title': "RSS"})
    assert link_obj
    return cast(str, link_obj["href"])

def get_feed_details(url: str) -> Dict[str, Any]:
    feed = parse(url).feed
    return {
        'id': feed["id"],
        'link': feed["links"][0]["href"],
        'title': feed["title"],
    }

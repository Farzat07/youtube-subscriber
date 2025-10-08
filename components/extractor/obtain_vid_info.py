from urllib.request import urlopen

from bs4 import BeautifulSoup
from isodate import parse_duration # type: ignore

def obtain_vid_duration(url: str, html: str = '') -> int:
    html = html or urlopen(url).read().decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')

    duration_meta = soup.find('meta', itemprop='duration')
    assert duration_meta
    duration = parse_duration(duration_meta['content'])
    return int(duration.total_seconds())

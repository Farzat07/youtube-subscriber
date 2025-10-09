from sys import stderr
from traceback import print_exc
from urllib.request import urlopen

from bs4 import BeautifulSoup
from isodate import parse_duration # type: ignore
from requests import get

def obtain_vid_duration(url: str, vid_id: str, html: str='', api_key: str='') -> int:
    if api_key:
        try:
            data = get("https://www.googleapis.com/youtube/v3/videos", params={
                'part': "contentDetails",
                'id': vid_id[9:],
                'key': api_key,
            }).json()
            duration_str = data['items'][0]['contentDetails']['duration']
            print(vid_id[9:], duration_str)
            return int(parse_duration(duration_str).total_seconds())
        except:
            print("Web scraping will be used due to an error with the following id:", vid_id, file=stderr)
            print_exc()
    html = html or urlopen(url).read().decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')

    duration_meta = soup.find('meta', itemprop='duration')
    assert duration_meta
    duration = parse_duration(duration_meta['content'])
    return int(duration.total_seconds())

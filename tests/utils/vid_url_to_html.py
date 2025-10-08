from urllib.parse import urlparse, parse_qs

from components.extractor.check_url import is_video
from .get_random_vid_info import get_random_vid_duration

def extract_vid_id(url: str) -> str:
    if not is_video(url):
        raise Exception(url + " is not a YouTube video URL")
    parsed_url = urlparse(url)
    if parsed_url.netloc == 'youtu.be':
        return parsed_url.path[1:]
    if parsed_url.path == '/watch':
        query_params = parse_qs(parsed_url.query)
        return query_params['v'][0]
    return parsed_url.path.split('/')[-1]

def get_vid_html_from_url(url: str) -> str:
    with open(f'tests/data/video@{extract_vid_id(url)}.html', 'r') as file:
        return file.read()

def obtain_vid_duration(url:str, html: str = '') -> int:
    return get_random_vid_duration(url)

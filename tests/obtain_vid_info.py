from unittest import TestCase

from components.extractor.obtain_vid_info import obtain_vid_duration
from .utils.vid_url_to_html import get_vid_html_from_url

class TestObtainVidInfo(TestCase):
    def test_obtain_vid_duration_from_shorts(self) -> None:
        url = "https://www.youtube.com/shorts/iD1Z7ccGyhk"
        self.assertEqual(60, obtain_vid_duration(url, '', html=get_vid_html_from_url(url)))

    def test_obtain_vid_duration_from_videos(self) -> None:
        url = "https://www.youtube.com/watch?v=WI4U1SVIO3I"
        self.assertEqual(8*60+11, obtain_vid_duration(url, '', html=get_vid_html_from_url(url)))

    def test_obtain_vid_duration_from_videos_with_params(self) -> None:
        url = "https://www.youtube.com/watch?v=k7RM-ot2NWY&list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab&index=2&pp=iAQB"
        self.assertEqual(9*60+59, obtain_vid_duration(url, '', html=get_vid_html_from_url(url)))

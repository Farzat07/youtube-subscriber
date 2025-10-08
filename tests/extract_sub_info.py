from unittest import TestCase
from unittest.mock import MagicMock, patch

from components.extractor.extract_sub_info import get_feed_details, get_channel_feed, get_playlist_feed

class TestExtractSubInfo(TestCase):
    def test_get_feed_details(self) -> None:
        self.assertEqual(get_feed_details("tests/data/feed@gentoo@mentaloutlaw@001.xml"), {
            "id": "yt:playlist:PL3cu45aM3C2CADmCYeVhS4KTVut9MoMc9",
            "link": "http://www.youtube.com/feeds/videos.xml?playlist_id=PL3cu45aM3C2CADmCYeVhS4KTVut9MoMc9",
            "title": "Gentoo",
        })
        self.assertEqual(get_feed_details("tests/data/feed@mentaloutlaw@001.xml"), {
            "id": "yt:channel:7YOGHUfC1Tb6E4pudI9STA",
            "link": "http://www.youtube.com/feeds/videos.xml?channel_id=UC7YOGHUfC1Tb6E4pudI9STA",
            "title": "Mental Outlaw",
        })
        self.assertEqual(get_feed_details("tests/data/feed@ytnnews24@001.xml"), {
            "id": "yt:channel:hlgI3UHCOnwUGzWzbJ3H5w",
            "link": "http://www.youtube.com/feeds/videos.xml?channel_id=UChlgI3UHCOnwUGzWzbJ3H5w",
            "title": "YTN",
        })
        self.assertEqual(get_feed_details("tests/data/feed@ytnnews24@002.xml"), {
            "id": "yt:channel:hlgI3UHCOnwUGzWzbJ3H5w",
            "link": "http://www.youtube.com/feeds/videos.xml?channel_id=UChlgI3UHCOnwUGzWzbJ3H5w",
            "title": "YTN",
        })

    def test_get_channel_feed(self) -> None:
        with open("tests/data/channel@aljazeera.html", 'r') as file:
            channel_html = file.read()
        self.assertEqual("https://www.youtube.com/feeds/videos.xml?channel_id=UCfiwzLy-8yKzIbsmZTzxDgw",
                         get_channel_feed(url='https://www.youtube.com/@aljazeera', html=channel_html))
        for tab in ('videos', 'shorts', 'streams', 'playlists', 'posts'):
            with open("tests/data/channel@rossmanngroup@%s.html" % tab, 'r') as file:
                channel_html = file.read()
            self.assertEqual("https://www.youtube.com/feeds/videos.xml?channel_id=UCl2mFZoRqjw_ELax4Yisf6w",
                             get_channel_feed('https://www.youtube.com/@rossmanngroup/'+tab, html=channel_html))

    def test_get_playlist_feed(self) -> None:
        self.assertEqual(get_playlist_feed("https://www.youtube.com/watch?v=kYB8IZa5AuE&list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab&index=3"),
                         "https://www.youtube.com/feeds/videos.xml?playlist_id=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab")
        self.assertEqual(get_playlist_feed("https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab"),
                         "https://www.youtube.com/feeds/videos.xml?playlist_id=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab")

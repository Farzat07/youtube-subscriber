from unittest import TestCase

from components.extractor.check_url import is_youtube, is_channel, is_playlist, is_video

class Test_URL_Checker(TestCase):
    def test_youtube_detection(self) -> None:
        self.assertTrue(is_youtube("https://www.youtube.com/watch?v=dQw4w9WgXcQ"))
        self.assertFalse(is_youtube("https://archive.org/"))
        self.assertTrue(is_youtube("https://www.youtube.com/c/3blue1brown"))
        self.assertFalse(is_youtube("https://www.nasa.gov/"))
        self.assertTrue(is_youtube("https://youtu.be/jNQXAC9IVRw"))
        self.assertFalse(is_youtube("https://www.wikipedia.org/"))
        self.assertFalse(is_youtube("https://www.youtube.com/")) # Nothing after the domain.
        self.assertFalse(is_youtube("https://xkcd.com/"))
        self.assertTrue(is_youtube("https://www.youtube.com/@kurzgesagt"))
        self.assertFalse(is_youtube("https://www.gutenberg.org/"))

    def test_channel_detection(self) -> None:
        self.assertTrue(is_channel("https://www.youtube.com/@LexFridman"))
        self.assertTrue(is_channel("https://www.youtube.com/@PrimitiveTechnology"))
        self.assertTrue(is_channel("https://www.youtube.com/user/schafer5"))
        self.assertTrue(is_channel("https://www.youtube.com/channel/UCBa659QWEk1AI4Tg--mrJ2A"))
        self.assertTrue(is_channel("https://www.youtube.com/c/mkbhd"))
        self.assertTrue(is_channel("https://www.youtube.com/@MentalOutlaw/videos"))
        self.assertFalse(is_channel("https://youtu.be/jNQXAC9IVRw"))
        self.assertFalse(is_channel("https://www.youtube.com/watch?v=dQw4w9WgXcQ"))
        self.assertFalse(is_channel("https://www.youtube.com/playlist?list=PL3cu45aM3C2CADmCYeVhS4KTVut9MoMc9"))

    def test_playlist_detection(self) -> None:
        self.assertTrue(is_playlist("https://www.youtube.com/playlist?list=PLZHQObOWTQDMsr9K-rj53DwVRMYO3t5Yr"))
        self.assertTrue(is_playlist("https://www.youtube.com/watch?v=YykjpeuMNEk&list=PLirAqAtl_h2r5g8xGajEwdXd3x1sZh8hC&index=1&t=245s"))
        self.assertFalse(is_playlist("https://www.youtube.com/@LexFridman"))
        self.assertFalse(is_playlist("https://www.youtube.com/watch?v=dQw4w9WgXcQ"))

    def test_video_detection(self) -> None:
        self.assertTrue(is_video("https://youtu.be/G8iEMVr7GFg?t=112"))
        self.assertTrue(is_video("https://www.youtube.com/watch?v=dQw4w9WgXcQ"))
        self.assertTrue(is_video("https://youtu.be/jNQXAC9IVRw"))
        self.assertFalse(is_video("https://www.youtube.com/channel/UCBa659QWEk1AI4Tg--mrJ2A"))
        self.assertFalse(is_video("https://www.youtube.com/playlist?list=PLZHQObOWTQDMsr9K-rj53DwVRMYO3t5Yr"))

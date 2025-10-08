from typing import Any, Dict
from unittest import TestCase
from unittest.mock import MagicMock, patch

from mongomock import MongoClient
from pymongo.collection import Collection

from components.subscriptions.main import Subscription
from components.subscriptions.typing import SubsDict
from components.videos import VideoTuple
from data_analyser.utils import analyse_video, analyse_subscription, analyse_collection
from .utils.vid_url_to_html import obtain_vid_duration
from .utils.get_random_vid_info import get_random_vid_duration

class TestAnalyser(TestCase):
    def setUp(self) -> None:
        self.client: MongoClient[Any] = MongoClient(tz_aware=True)
        self.collection: Collection[SubsDict] = self.client.db.collection

        self.sub1 = Subscription(
            _id="yt:channel:hlgI3UHCOnwUGzWzbJ3H5w",
            link=r"tests/data/feed@ytnnews24@001.xml",
            time_between_fetches=1,
        )
        self.sub1._collection = self.collection
        self.sub1.insert()
        self.sub1.fetch()

        self.mock_vid_duration = patch('data_analyser.utils.obtain_vid_duration').start()
        self.mock_vid_duration.side_effect = obtain_vid_duration
        self.addCleanup(patch.stopall)

    def test_analyse_video(self) -> None:
        modified_vid = analyse_video(self.sub1.videos[1])

        expected_duration = get_random_vid_duration(self.sub1.videos[1].link)
        self.assertIsInstance(modified_vid, VideoTuple)
        self.assertEqual(modified_vid.duration, expected_duration)
        self.assertTrue(modified_vid.analysed)

    def test_analyse_video_with_exception(self) -> None:
        self.mock_vid_duration.side_effect = Exception("Network error")

        modified_vid = analyse_video(self.sub1.videos[0])
        self.assertIsInstance(modified_vid, VideoTuple)
        self.assertLess(modified_vid.duration, 0)
        self.assertTrue(modified_vid.analysed)

    def test_analyse_subscription(self) -> None:
        self.assertTrue(analyse_subscription(self.sub1))
        for vid in self.sub1.videos:
            expected_duration = get_random_vid_duration(vid.link)
            self.assertEqual(vid.duration, expected_duration)
            self.assertTrue(vid.analysed)

    def test_analyse_subscription_with_further_fetch(self) -> None:
        self.assertTrue(analyse_subscription(self.sub1))
        for vid in self.sub1.videos:
            expected_duration = get_random_vid_duration(vid.link)
            self.assertEqual(vid.duration, expected_duration)
            self.assertTrue(vid.analysed)
        self.sub1.link = r"tests/data/feed@ytnnews24@002.xml"
        self.sub1.fetch()
        self.assertTrue(analyse_subscription(self.sub1))
        for vid in self.sub1.videos:
            expected_duration = get_random_vid_duration(vid.link)
            self.assertEqual(vid.duration, expected_duration)
            self.assertTrue(vid.analysed)

    def test_analyse_subscription_without_further_fetch(self) -> None:
        self.assertTrue(analyse_subscription(self.sub1))
        for vid in self.sub1.videos:
            expected_duration = get_random_vid_duration(vid.link)
            self.assertEqual(vid.duration, expected_duration)
            self.assertTrue(vid.analysed)
        self.assertFalse(analyse_subscription(self.sub1))

    def test_analyse_collection(self) -> None:
        self.assertEqual(analyse_collection(self.collection), 1)
        for sub_dict in self.collection.find():
            for vid in map(VideoTuple._make, sub_dict["videos"]):
                expected_duration = get_random_vid_duration(vid.link)
                self.assertEqual(vid.duration, expected_duration)
                self.assertTrue(vid.analysed)
        self.sub2 = Subscription(
            _id="yt:channel:7YOGHUfC1Tb6E4pudI9STA",
            link=r"tests/data/feed@mentaloutlaw@001.xml",
            time_between_fetches=1,
        )
        self.sub2._collection = self.collection
        self.sub2.insert()
        self.sub2.fetch()
        self.assertEqual(analyse_collection(self.collection), 1)
        for sub_dict in self.collection.find():
            sub = Subscription(**sub_dict)
            for vid in map(VideoTuple._make, sub_dict["videos"]):
                expected_duration = get_random_vid_duration(vid.link)
                self.assertEqual(vid.duration, expected_duration)
                self.assertTrue(vid.analysed)

    def tearDown(self) -> None:
        self.client.close()

from hashlib import md5
from typing import Any, Dict
from unittest import TestCase
from unittest.mock import MagicMock, patch

from mongomock import MongoClient
from pymongo.collection import Collection

from components.subscriptions.main import Subscription
from components.subscriptions.typing import SubsDict
from components.videos import VideoTuple
from components.ytdlp import obtain_vid_info
from data_analyser.utils import analyse_video, analyse_subscription, analyse_collection

def url_based_extract_info(url: str, **_: Any) -> Dict[str, Any]:
    hash = md5(url.encode()).hexdigest()
    hash_int = int(hash[:4], 16)
    seconds = hash_int %  60
    minutes = hash_int // 60
    hours   = minutes  // 60
    minutes = minutes  %  60
    if hours:
        duration_string = "%d:%02d:%02d" % (hours, minutes, seconds)
    elif minutes:
        duration_string = "%d:%02d" % (minutes, seconds)
    else:
        duration_string = "%d" % (seconds, )
    return {
        "duration_string": duration_string,
        "other_key": "other_value",
        "other key": "other value",
    }

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

        self.mock_ydl_class = patch('components.ytdlp.YoutubeDL').start()
        self.mock_ydl_instance = MagicMock()
        self.mock_ydl_class.return_value.__enter__.return_value = self.mock_ydl_instance
        self.mock_ydl_instance.extract_info.side_effect = url_based_extract_info
        self.addCleanup(patch.stopall)

    def test_obtain_vid_info(self) -> None:
        result = obtain_vid_info(self.sub1.videos[0].link)
        expected_duration = url_based_extract_info(self.sub1.videos[0].link)["duration_string"]
        self.assertEqual(result, {"duration_string": expected_duration})

    def test_obtain_vid_info_with_exception(self) -> None:
        self.mock_ydl_instance.extract_info.side_effect = Exception("Network error")

        result = obtain_vid_info(self.sub1.videos[0].link)
        expected_keys = {"duration_string"}
        actual_keys = set(result.keys())
        self.assertEqual(expected_keys, actual_keys,
                         "Expected keys %s, got %s." % (expected_keys, actual_keys))
        self.assertRegex(result["duration_string"], "^-1:[0-5][0-9]$")

    def test_analyse_video(self) -> None:
        modified_vid = analyse_video(self.sub1.videos[1])

        expected_duration = url_based_extract_info(self.sub1.videos[1].link)["duration_string"]
        self.assertIsInstance(modified_vid, VideoTuple)
        self.assertEqual(modified_vid.duration_string, expected_duration)
        self.assertTrue(modified_vid.analysed)

    def test_analyse_video_with_exception(self) -> None:
        self.mock_ydl_instance.extract_info.side_effect = Exception("Network error")

        modified_vid = analyse_video(self.sub1.videos[0])
        self.assertIsInstance(modified_vid, VideoTuple)
        self.assertRegex(modified_vid.duration_string, "^-1:[0-5][0-9]$")
        self.assertTrue(modified_vid.analysed)

    def test_analyse_subscription(self) -> None:
        self.assertTrue(analyse_subscription(self.sub1))
        for vid in self.sub1.videos:
            expected_duration = url_based_extract_info(vid.link)["duration_string"]
            self.assertEqual(vid.duration_string, expected_duration)
            self.assertTrue(vid.analysed)

    def test_analyse_subscription_with_further_fetch(self) -> None:
        self.assertTrue(analyse_subscription(self.sub1))
        for vid in self.sub1.videos:
            expected_duration = url_based_extract_info(vid.link)["duration_string"]
            self.assertEqual(vid.duration_string, expected_duration)
            self.assertTrue(vid.analysed)
        self.sub1.link = r"tests/data/feed@ytnnews24@002.xml"
        self.sub1.fetch()
        self.assertTrue(analyse_subscription(self.sub1))
        for vid in self.sub1.videos:
            expected_duration = url_based_extract_info(vid.link)["duration_string"]
            self.assertEqual(vid.duration_string, expected_duration)
            self.assertTrue(vid.analysed)

    def test_analyse_subscription_without_further_fetch(self) -> None:
        self.assertTrue(analyse_subscription(self.sub1))
        for vid in self.sub1.videos:
            expected_duration = url_based_extract_info(vid.link)["duration_string"]
            self.assertEqual(vid.duration_string, expected_duration)
            self.assertTrue(vid.analysed)
        self.assertFalse(analyse_subscription(self.sub1))

    def test_analyse_collection(self) -> None:
        self.assertEqual(analyse_collection(self.collection), 1)
        for sub_dict in self.collection.find():
            for vid in map(VideoTuple._make, sub_dict["videos"]):
                expected_duration = url_based_extract_info(vid.link)["duration_string"]
                self.assertEqual(vid.duration_string, expected_duration)
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
                expected_duration = url_based_extract_info(vid.link)["duration_string"]
                self.assertEqual(vid.duration_string, expected_duration)
                self.assertTrue(vid.analysed)

    def tearDown(self) -> None:
        self.client.close()

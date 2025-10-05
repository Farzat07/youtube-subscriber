from typing import Any
from mongomock import MongoClient
from pymongo.collection import Collection
from unittest import TestCase
from components.subscriptions.main import Subscription
from components.subscriptions.typing import SubsDict
from components.users.typing import UserDict


class TestFeeds(TestCase):
    def setUp(self) -> None:
        self.client: MongoClient[Any] = MongoClient(tz_aware=True)
        self.collection: Collection[SubsDict] = self.client.db.collection

    def test_insert(self) -> None:
        sub = Subscription(
            _id="yt:channel:bla",
            link="http://www.youtube.com/feeds/videos.xml?channel_id=UCbla",
            time_between_fetches=5,
        )
        sub._collection = self.collection
        sub.insert()
        sub_dict = self.collection.find_one({"_id": "yt:channel:bla"})
        self.assertIsNotNone(sub_dict)
        assert sub_dict # To appease mypy.
        self.assertDictEqual(sub.asdict(), sub_dict)

    def test_feed_fetch(self) -> None:
        sub = Subscription(
            _id="yt:channel:hlgI3UHCOnwUGzWzbJ3H5w",
            link=r"tests/data/feed@ytnnews24@001.xml",
            time_between_fetches=1,
        )
        sub._collection = self.collection
        sub.insert()
        sub.fetch()
        self.assertEqual(15, len(sub.videos))
        sub_dict = self.collection.find_one({"_id": "yt:channel:hlgI3UHCOnwUGzWzbJ3H5w"})
        self.assertIsNotNone(sub_dict)
        assert sub_dict # To appease mypy.
        self.assertEqual(15, len(sub_dict["videos"]))

    def test_feed_update(self) -> None:
        sub = Subscription(
            _id="yt:channel:hlgI3UHCOnwUGzWzbJ3H5w",
            link=r"tests/data/feed@ytnnews24@001.xml",
            time_between_fetches=1,
        )
        sub._collection = self.collection
        sub.insert()
        sub.fetch()
        sub.link=r"tests/data/feed@ytnnews24@002.xml"
        sub.fetch()
        self.assertEqual(16, len(sub.videos))
        sub_dict = self.collection.find_one({"_id": "yt:channel:hlgI3UHCOnwUGzWzbJ3H5w"})
        self.assertIsNotNone(sub_dict)
        assert sub_dict # To appease mypy.
        self.assertEqual(16, len(sub_dict["videos"]))

    def tearDown(self) -> None:
        self.client.close()

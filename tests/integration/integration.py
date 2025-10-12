from os import getenv
from unittest import TestCase

from components.database import subscriptions
from data_analyser.utils import analyse_collection
from data_collector.utils import collect_data
from wsgi import app

class TestIntegration(TestCase):
    def setUp(self) -> None:
        app.config['TESTING'] = True
        self.client = app.test_client()
        subscriptions.delete_many({})
        self.client.post("/add-sub/", data={
            'url': "https://www.youtube.com/playlist?list=PLZmiPrHYOIsRtlMRPjLd5WhmM8BddIdj0",
            'time_between_fetches': 1,
        })

    def test_collection_and_analyses(self) -> None:
        # Confirm that the playlist exists but there are not videos stored yet.
        response = self.client.get("/vid-from-link/yt:playlist:PLZmiPrHYOIsRtlMRPjLd5WhmM8BddIdj0")
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertListEqual(response_data, [])

        collect_data(subscriptions)
        # Confirm that the videos now exist but are not analysed yet.
        response = self.client.get("/vid-from-link/yt:playlist:PLZmiPrHYOIsRtlMRPjLd5WhmM8BddIdj0")
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertEqual(len(response_data), 1)
        for vid in response_data:
            self.assertFalse(vid["analysed"])

        self.assertEqual(1, analyse_collection(subscriptions, getenv("YOUTUBE_API_KEY") or '')
)
        # Confirm that the videos now exist and has a valid duration.
        response = self.client.get("/vid-from-link/yt:playlist:PLZmiPrHYOIsRtlMRPjLd5WhmM8BddIdj0")
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertEqual(len(response_data), 1)
        for vid in response_data:
            self.assertTrue(vid["analysed"])
            self.assertGreaterEqual(vid["duration"], 0)

    def tearDown(self) -> None:
        subscriptions.delete_many({})

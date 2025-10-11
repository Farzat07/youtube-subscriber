from unittest import TestCase

from components.database import subscriptions
from wsgi import app

class TestFlask(TestCase):
    def setUp(self) -> None:
        app.config['TESTING'] = True
        self.client = app.test_client()
        subscriptions.delete_many({})

    def test_add_sub(self) -> None:
        # A valid channel - should succeed.
        response = self.client.post("/add-sub/", data={
            'url': "https://www.youtube.com/channel/UCBa659QWEk1AI4Tg--mrJ2A",
            'time_between_fetches': 3123,
        })
        self.assertEqual(response.status_code, 201)
        # Duplicate - should return 409.
        response = self.client.post("/add-sub/", data={
            'url': "https://www.youtube.com/channel/UCBa659QWEk1AI4Tg--mrJ2A",
            'time_between_fetches': 532,
        })
        self.assertEqual(response.status_code, 409)
        # A madeup channel - should return 400.
        response = self.client.post("/add-sub/", data={
            'url': "https://www.youtube.com/channel/UCBa659QWEk14Tg--mrJ2A",
            'time_between_fetches': 6824,
        })
        self.assertEqual(response.status_code, 400)
        # Integer strings are accepted for time_between_fetches.
        response = self.client.post("/add-sub/", data={
            'url': "https://www.youtube.com/playlist?list=PLZHQObOWTQDMsr9K-rj53DwVRMYO3t5Yr",
            'time_between_fetches': "622",
        })
        self.assertEqual(response.status_code, 201)
        # An invalid duration - should return 400.
        response = self.client.post("/add-sub/", data={
            'url': "https://www.youtube.com/channel/UCBa659QWEk1AI4Tg--mrJ2A",
            'time_between_fetches': "32.2",
        })
        self.assertEqual(response.status_code, 400)
        # An invalid subscription - should return 400.
        response = self.client.post("/add-sub/", data={
            'url': "https://www.youtube.com/watch?v=WI4U1SVIO3I",
            'time_between_fetches': 132,
        })
        self.assertEqual(response.status_code, 400)
        # A valid channel - should succeed.
        response = self.client.post("/add-sub/", data={
            'url': "https://www.youtube.com/@MentalOutlaw/videos",
            'time_between_fetches': 234,
        })
        self.assertEqual(response.status_code, 201)
        # A valid playlist - should succeed.
        response = self.client.post("/add-sub/", data={
            'url': "https://www.youtube.com/watch?v=kYB8IZa5AuE&list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab&index=3",
            'time_between_fetches': 231,
        })
        self.assertEqual(response.status_code, 201)
        # A duplicate despite the structure of the url being different.
        response = self.client.post("/add-sub/", data={
            'url': "https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab",
            'time_between_fetches': 2380,
        })
        self.assertEqual(response.status_code, 409)

    def tearDown(self) -> None:
        subscriptions.delete_many({})

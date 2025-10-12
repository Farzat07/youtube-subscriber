from datetime import datetime, UTC
from unittest import TestCase

from werkzeug.http import parse_date

from api import app
from components.database import subscriptions

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

    def test_subs_info(self) -> None:
        # Should be empty at start.
        response = self.client.get("/subs-info")
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertListEqual(response_data, [])
        # Fetching any individual subscription now should fail.
        response = self.client.get("/sub-info/yt:channel:Ba659QWEk1AI4Tg--mrJ2A")
        self.assertEqual(response.status_code, 404)
        # Fetching the videos of an individual subscription should also fail.
        response = self.client.get("/vid-from-link/yt:channel:Ba659QWEk1AI4Tg--mrJ2A")
        self.assertEqual(response.status_code, 404)
        # Now add some data to test on...
        self.client.post("/add-sub/", data={
            'url': "https://www.youtube.com/channel/UCBa659QWEk1AI4Tg--mrJ2A",
            'time_between_fetches': 1,
        })
        self.client.post("/add-sub/", data={
            'url': "https://www.youtube.com/playlist?list=PLZHQObOWTQDMsr9K-rj53DwVRMYO3t5Yr",
            'time_between_fetches': 1,
        })
        # Now should contain 2 subscriptions.
        response = self.client.get("/subs-info")
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertEqual(len(response_data), 2)
        for sub_info in response_data:
            self.assertEqual(sub_info["videos"], 0)
        # Now fetching an added subscriptions should work.
        response = self.client.get("/sub-info/yt:channel:Ba659QWEk1AI4Tg--mrJ2A")
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertEqual(response_data["_id"], "yt:channel:Ba659QWEk1AI4Tg--mrJ2A")
        # Same for its videos - though they should still be empty.
        response = self.client.get("/vid-from-link/yt:channel:Ba659QWEk1AI4Tg--mrJ2A")
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertListEqual(response_data, [])
        # Subscriptions not added should still not work.
        response = self.client.get("/sub-info/yt:channel:7YOGHUfC1Tb6E4pudI9STA")
        self.assertEqual(response.status_code, 404)
        # Same for for their videos.
        response = self.client.get("/vid-from-link/yt:channel:7YOGHUfC1Tb6E4pudI9STA")
        self.assertEqual(response.status_code, 404)

    def test_modify_subs(self) -> None:
        # Confirm all methods do not work before the item exists.
        response = self.client.patch("/set-time-between-fetches/yt:channel:Ba659QWEk1AI4Tg--mrJ2A", data={
            'time_between_fetches': 313,
        })
        self.assertEqual(response.status_code, 404)
        response = self.client.patch("/set-viewed/yt:channel:Ba659QWEk1AI4Tg--mrJ2A", data={
            'viewed_time': datetime.now(tz=UTC).isoformat(),
        })
        self.assertEqual(response.status_code, 404)
        response = self.client.delete("/delete-sub/yt:channel:Ba659QWEk1AI4Tg--mrJ2A")
        self.assertEqual(response.status_code, 404)
        # Now add some data to test on...
        self.client.post("/add-sub/", data={
            'url': "https://www.youtube.com/channel/UCBa659QWEk1AI4Tg--mrJ2A",
            'time_between_fetches': 1,
        })
        # Test set-time-between-fetches.
        response = self.client.patch("/set-time-between-fetches/yt:channel:Ba659QWEk1AI4Tg--mrJ2A", data={
            'time_between_fetches': 31323,
        })
        self.assertEqual(response.status_code, 200)
        # Should not work if an integer is not provided.
        response = self.client.patch("/set-time-between-fetches/yt:channel:Ba659QWEk1AI4Tg--mrJ2A", data={
            'time_between_fetches': 31.3,
        })
        self.assertEqual(response.status_code, 400)
        # Test set-viewed.
        update_time_to = datetime.now(tz=UTC)
        response = self.client.patch("/set-viewed/yt:channel:Ba659QWEk1AI4Tg--mrJ2A", data={
            'viewed_time': update_time_to.isoformat(),
        })
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertEqual(update_time_to.replace(microsecond=0), parse_date(response_data["last_viewed"]))
        # Should not work with an invalid datetime string.
        response = self.client.patch("/set-viewed/yt:channel:Ba659QWEk1AI4Tg--mrJ2A", data={
            'viewed_time': "Monday 11th of February 2023",
        })
        self.assertEqual(response.status_code, 400)
        # Should work fine without a viewed_time set though...
        time_before_updating = datetime.now(tz=UTC)
        response = self.client.patch("/set-viewed/yt:channel:Ba659QWEk1AI4Tg--mrJ2A")
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        last_viewed = parse_date(response_data["last_viewed"])
        assert last_viewed
        self.assertLessEqual(time_before_updating.replace(microsecond=0), last_viewed)
        # Delete the subscription.
        response = self.client.delete("/delete-sub/yt:channel:Ba659QWEk1AI4Tg--mrJ2A")
        self.assertEqual(response.status_code, 200)
        # Make sure the item no longer exists.
        response = self.client.get("/sub-info/yt:channel:Ba659QWEk1AI4Tg--mrJ2A")
        self.assertEqual(response.status_code, 404)

    def tearDown(self) -> None:
        subscriptions.delete_many({})

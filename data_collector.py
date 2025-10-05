#!/usr/bin/env python

from time import sleep
from datetime import datetime, timedelta, UTC
from components.database import subscriptions
from components.subscriptions.main import Subscription

while True:
    for sub_dict in subscriptions.find():
        sub = Subscription(**sub_dict)
        if datetime.now(tz=UTC) - sub.last_fetch > timedelta(seconds=sub.time_between_fetches):
            sub.fetch()
    sleep(60)

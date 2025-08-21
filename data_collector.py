#!/usr/bin/env python

from time import sleep
from components.database import subscriptions
from components.subscriptions.main import Subscription, default_scheduler

subs_to_fetch = ["fiwzLy-8yKzIbsmZTzxDgw", "Ef0-WZoqYFzLZtx43KPvag",
                 "PF-oYb2-xN5FbCXy0167Gg", "hlgI3UHCOnwUGzWzbJ3H5w", ]
for id in subs_to_fetch:
    sub_dict = subscriptions.find_one({"_id": "yt:channel:"+id})
    if sub_dict:
        sub = Subscription(**sub_dict)
    else:
        sub = Subscription(
            _id="yt:channel:"+id,
            link="http://www.youtube.com/feeds/videos.xml?channel_id=UC"+id,
            time_between_fetches=5,
        )
        sub.insert()
    sub.initialise_job()

while True:
    default_scheduler.run_pending()
    sleep(60)

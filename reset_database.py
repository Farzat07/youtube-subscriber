#!/usr/bin/env python

from time import sleep
from components.database import subscriptions
from components.subscriptions.main import Subscription
from components.videos import VideoTuple

subscriptions.delete_many({})
for short_id in ['fiwzLy-8yKzIbsmZTzxDgw', 'Ef0-WZoqYFzLZtx43KPvag',
                 'PF-oYb2-xN5FbCXy0167Gg', 'hlgI3UHCOnwUGzWzbJ3H5w', ]:
    sub = Subscription(
        _id='yt:channel:'+short_id,
        link='http://www.youtube.com/feeds/videos.xml?channel_id=UC'+short_id,
        time_between_fetches=300,
    )
    sub.insert()

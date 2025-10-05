#!/usr/bin/env python

from time import sleep

from components.database import subscriptions
from components.subscriptions.main import Subscription
from components.subscriptions.typing import SubsDict
from components.videos import VideoTuple
from components.ytdlp import obtain_vid_info

from pymongo.collection import Collection

def analyse_video(vid_tuple: VideoTuple) -> VideoTuple:
    info = obtain_vid_info(vid_tuple.link)
    return vid_tuple._replace(analysed=True, duration_string=info["duration_string"])

def analyse_subscription(sub: Subscription) -> bool:
    updated = False
    for i, vid in enumerate(sub.videos):
        if not vid.analysed:
            sub.videos[i] = analyse_video(vid)
            updated = True
    return updated

def analyse_collection(subs_collection: Collection[SubsDict]) -> None:
    for sub_dict in subs_collection.find():
        sub = Subscription(**sub_dict)
        if analyse_subscription(sub):
            sub.update_videos()

while True:
    analyse_collection(subscriptions)
    sleep(30)

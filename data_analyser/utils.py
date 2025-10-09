from traceback import print_exc

from pymongo.collection import Collection

from components.subscriptions.main import Subscription
from components.subscriptions.typing import SubsDict
from components.videos import VideoTuple
from components.extractor.obtain_vid_info import obtain_vid_duration

def analyse_video(vid_tuple: VideoTuple, api_key: str='') -> VideoTuple:
    try:
        duration = obtain_vid_duration(vid_tuple.link, vid_tuple.id, api_key=api_key)
    except:
        print_exc()
        duration = -2
    return vid_tuple._replace(analysed=True, duration=duration)

def analyse_subscription(sub: Subscription, api_key: str='') -> bool:
    updated = False
    for i, vid in enumerate(sub.videos):
        if not vid.analysed:
            sub.videos[i] = analyse_video(vid, api_key)
            updated = True
    return updated

def analyse_collection(subs_collection: Collection[SubsDict], api_key: str='') -> int:
    num_updated = 0
    for sub_dict in subs_collection.find():
        sub = Subscription(**sub_dict)
        sub._collection = subs_collection
        if analyse_subscription(sub, api_key):
            sub.update_videos()
            num_updated += 1
    return num_updated

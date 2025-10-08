from datetime import datetime
from typing import TypedDict, List
from bson.objectid import ObjectId
from components.videos import VideoTuple

class SubsDict(TypedDict):
    _id: str
    link: str
    title: str
    time_between_fetches: int # In seconds.
    last_fetch: datetime
    last_video_update: datetime
    last_viewed: datetime
    videos: List[VideoTuple]
    subscribers: List[ObjectId]

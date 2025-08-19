from datetime import datetime
from typing import TypedDict, List
from bson.objectid import ObjectId
from components.videos import VideoTuple

class SubsDict(TypedDict):
    id: str
    link: str
    time_between_fetches: int # In hours.
    last_update: datetime
    videos: List[VideoTuple]
    subscribers: List[ObjectId]

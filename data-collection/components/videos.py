from typing import NamedTuple
from datetime import datetime

class VideoTuple(NamedTuple):
    id: str
    link: str
    title: str
    published: datetime
    updated: datetime
    thumbnail: str
    summary: str

from dataclasses import dataclass, field
from datetime import datetime
from sys import stderr
from typing import TypedDict, List
from bson.objectid import ObjectId
from feedparser import parse # type: ignore
import requests
import schedule
from components.videos import VideoTuple

@dataclass
class Subscription:
    id: str
    link: str
    time_between_fetches: int
    last_update: datetime = datetime.min
    videos: List[VideoTuple] = field(default_factory=list)
    subscribers: List[ObjectId] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._job: schedule.Job = schedule.every(self.time_between_fetches).second.do(self.update)

    def update(self) -> None:
        try:
            for entry in parse(self.link)["entries"]:
                self.videos.append(VideoTuple(
                    id = entry.id,
                    link = entry.link,
                    title = entry.title,
                    published = datetime.fromisoformat(entry.published),
                    updated = datetime.fromisoformat(entry.updated),
                    thumbnail = entry.media_thumbnail[0]["url"],
                    summary = entry.summary,
                ))
        except Exception as e:
            print("Ran into exception", e, file=stderr)

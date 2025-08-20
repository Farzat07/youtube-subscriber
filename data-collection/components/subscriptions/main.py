from dataclasses import dataclass, field, asdict
from datetime import datetime, UTC
from sys import stderr
from typing import TypedDict, List
from bson.objectid import ObjectId
from feedparser import parse # type: ignore
from pymongo.collection import Collection
from pymongo.results import UpdateResult
import schedule
from components.database import subscriptions
from components.subscriptions.typing import SubsDict
from components.videos import VideoTuple

@dataclass
class Subscription:
    _id: str
    link: str
    time_between_fetches: int
    last_fetch: datetime = datetime.min.replace(tzinfo=UTC)
    last_video_update: datetime = datetime.min.replace(tzinfo=UTC)
    videos: List[VideoTuple] = field(default_factory=list)
    subscribers: List[ObjectId] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._job: schedule.Job = schedule.every(self.time_between_fetches).minutes.do(self.fetch)
        self._collection: Collection[SubsDict] = subscriptions
        self._in_db: bool = False

    def fetch(self) -> None:
        try:
            rss = parse(self.link)
        except Exception as e:
            print("Ran into an exception while fetching", self._id + ":", e, file=stderr)
            return
        for vid in map(VideoTuple.from_rss_entry, rss.entries):
            if vid.published > self.last_video_update:
                self.videos.append(vid)
            elif vid.updated > self.last_video_update:
                for i, old_vid in enumerate(self.videos):
                    if vid.id == old_vid.id:
                        self.videos[i] = vid
                        break
        last_video_update = max((vid.updated for vid in self.videos))
        if last_video_update > self.last_video_update:
            print("Updating", self._id)
            self.last_video_update = last_video_update
            self.update_fields(["videos", "last_video_update"])
        self.last_fetch = datetime.now(tz=UTC)

    def update_fields(self, fields: List[str]) -> UpdateResult:
        sub = asdict(self)
        if self._in_db:
            return self._collection.update_one(
                {"_id": self._id},
                {"$set": {key: sub[key] for key in fields}},
            )
        self._in_db = True
        return self._collection.replace_one({"_id": self._id}, sub, upsert=True)

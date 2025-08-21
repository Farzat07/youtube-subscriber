from dataclasses import dataclass, field, asdict
from datetime import datetime, UTC
from sys import stderr
from typing import TypedDict, List, cast, Dict, Any
from bson.objectid import ObjectId
from feedparser import parse # type: ignore
from pymongo.collection import Collection
from pymongo.results import InsertOneResult, UpdateResult
from schedule import Job, Scheduler
from components.database import subscriptions
from components.subscriptions.typing import SubsDict
from components.videos import VideoTuple

default_scheduler = Scheduler()

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
        self._collection: Collection[SubsDict] = subscriptions
        self._scheduler: Scheduler = default_scheduler
        if len(self.videos) and type(self.videos[0]) != VideoTuple:
            self.videos = [VideoTuple._make(vid) for vid in self.videos]

    def initialise_job(self) -> None:
        self._job: Job = self._scheduler.every(self.time_between_fetches).minutes.do(self.fetch)
        if self.last_fetch > datetime.min.replace(tzinfo=UTC):
            self._job.next_run += self.last_fetch - datetime.now(tz=UTC)

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
        self.last_fetch = datetime.now(tz=UTC)
        if last_video_update > self.last_video_update:
            print("Updating", self._id, end=", ")
            print("New vid count:", len(self.videos))
            self.last_video_update = last_video_update
            self.update_fetch(videos=True)
        else:
            self.update_fetch()
        print("Fetched", self._id, "at", self.last_fetch)

    def asdict(self) -> SubsDict:
        return cast(SubsDict, asdict(self))

    def insert(self) -> InsertOneResult:
        return self._collection.insert_one(self.asdict())

    def update_fetch(self, videos: bool=False) -> UpdateResult:
        updated_values: Dict[str, Any] = { "last_fetch": self.last_fetch, }
        if videos:
            updated_values["videos"] = self.videos
            updated_values["last_video_update"] = self.last_video_update
        return self._collection.update_one(
            {"_id": self._id},
            {"$set": updated_values},
        )

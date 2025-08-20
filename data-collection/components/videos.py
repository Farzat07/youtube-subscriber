from typing import NamedTuple, Any, Self
from datetime import datetime

class VideoTuple(NamedTuple):
    id: str
    link: str
    title: str
    published: datetime
    updated: datetime
    thumbnail: str
    summary: str

    @classmethod
    def from_rss_entry(cls, entry: Any) -> Self:
        return cls(
            id = entry.id,
            link = entry.link,
            title = entry.title,
            published = datetime.fromisoformat(entry.published),
            updated = datetime.fromisoformat(entry.updated),
            thumbnail = entry.media_thumbnail[0]["url"],
            summary = entry.summary,
        )

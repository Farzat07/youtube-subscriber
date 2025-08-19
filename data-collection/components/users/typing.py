from datetime import datetime
from typing import TypedDict, NamedTuple, List, Tuple
from bson.objectid import ObjectId

class SubscriptionItem(NamedTuple):
    id: str
    time_between_fetches: int
    last_viewed: datetime

class UserDict(TypedDict):
    id: ObjectId
    name: str
    subscriptions: List[SubscriptionItem]

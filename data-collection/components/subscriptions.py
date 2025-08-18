from types import TypedDict
from datetime import datetime

class SubscriptionDict(TypedDict):
    id: str
    link: str
    time_between_fetches: float # In hours.
    last_update: datetime

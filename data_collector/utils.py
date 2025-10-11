from datetime import datetime, timedelta, UTC

from pymongo.collection import Collection

from components.subscriptions.main import Subscription
from components.subscriptions.typing import SubsDict

def collect_data(subs_collection: Collection[SubsDict]) -> None:
    for sub_dict in subs_collection.find():
        sub = Subscription(**sub_dict)
        sub._collection = subs_collection
        if datetime.now(tz=UTC) - sub.last_fetch > timedelta(seconds=sub.time_between_fetches):
            sub.fetch()

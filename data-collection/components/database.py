import atexit
from typing import Any, Dict
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from components.subscriptions.typing import SubsDict
from components.users.typing import UserDict

client: MongoClient[Any] = MongoClient("mongodb://localhost", tz_aware=True)
database: Database[Any] = client.get_database("youtube")
subscriptions: Collection[SubsDict] = database.get_collection("subscriptions")
users: Collection[UserDict] = database.get_collection("users")

@atexit.register
def _cleanup() -> None:
    client.close()

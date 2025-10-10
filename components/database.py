import atexit
from os import getenv
from typing import Any, Dict
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from components.subscriptions.typing import SubsDict
from components.users.typing import UserDict

load_dotenv('.env')

client: MongoClient[Any] = MongoClient(
    "mongodb://%s:%s@localhost/admin" % (getenv('MONGO_USER'), getenv('MONGO_PASS')),
    tz_aware=True,
)
database: Database[Any] = client.get_database(getenv('YT_DB') or "youtube")
subscriptions: Collection[SubsDict] = database.get_collection("subscriptions")
users: Collection[UserDict] = database.get_collection("users")

@atexit.register
def _cleanup() -> None:
    client.close()

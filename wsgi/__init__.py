from datetime import datetime, UTC
from typing import Any, Dict, List
from components.database import subscriptions
from components.subscriptions.main import Subscription
from components.videos import VideoTuple
from flask import Flask, request
from flask_cors import CORS

from components.extractor.extract_sub_info import get_sub_info_from_yt_url
from .utils import vid_dicts_from_tuple_list, sub_info_from_dict

app = Flask(__name__)
CORS(app)

@app.route("/vid-from-link/<id>")
def videos_from_link(id: str) -> List[Dict[str, Any]]:
    sub_dict = subscriptions.find_one({"_id": id})
    assert sub_dict
    return vid_dicts_from_tuple_list(sub_dict["videos"])

@app.route("/sub-info/<id>")
def sub_dict(id: str) -> Dict[str, Any]:
    sub_dict = subscriptions.find_one({"_id": id})
    assert sub_dict
    return sub_info_from_dict(sub_dict)

@app.route("/subs-info")
def subs_info() -> List[Dict[str, Any]]:
    return [sub_info_from_dict(sub_dict) for sub_dict in subscriptions.find()]

@app.post("/add-sub/")
def add_sub() -> Dict[str, Any]:
    sub_info = get_sub_info_from_yt_url(request.form["url"])
    sub = Subscription(
        _id=sub_info["id"],
        link=sub_info["link"],
        title=sub_info["title"],
        time_between_fetches=int(request.form["time_between_fetches"]),
    )
    sub.insert()
    return sub_info_from_dict(sub.asdict())

@app.post("/set-time-between-fetches/")
def set_time_between_fetches() -> Dict[str, Any]:
    time_between_fetches = int(request.form["time_between_fetches"])
    result = subscriptions.update_one(
        {"_id": request.form["_id"]},
        {"$set": {"time_between_fetches": time_between_fetches}}
    )
    if not result.modified_count:
        raise Exception("Subscription %s not found" % request.form["_id"])
    return {
        "_id": request.form["_id"],
        "time_between_fetches": time_between_fetches,
    }

@app.delete("/delete-sub/<id>")
def delete_sub(id: str) -> Dict[str, Any]:
    result = subscriptions.delete_one({"_id": id})
    if not result.deleted_count:
        raise Exception("Subscription %s not found" % id)
    return { "_id": id, }

@app.post("/set-viewed/")
def set_viewed() -> Dict[str, Any]:
    viewed_time_str = request.form.get("viewed_time")
    if viewed_time_str:
        viewed_time = datetime.fromisoformat(viewed_time_str)
    else:
        viewed_time = datetime.now(tz=UTC)
    result = subscriptions.update_one(
        {"_id": request.form["_id"]},
        {"$set": {"last_viewed": viewed_time}}
    )
    if not result.modified_count:
        raise Exception("Subscription %s not found" % request.form["_id"])
    return {
        "_id": request.form["_id"],
        "last_viewed": viewed_time,
    }

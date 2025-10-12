from datetime import datetime, UTC
from typing import Any, Dict, List, Tuple

from flask import Flask, request
from flask_cors import CORS
from pymongo.errors import DuplicateKeyError

from components.database import subscriptions
from components.subscriptions.main import Subscription
from components.videos import VideoTuple
from components.extractor.extract_sub_info import get_sub_info_from_yt_url
from .utils import vid_dicts_from_tuple_list, sub_info_from_dict

app = Flask(__name__)
CORS(app)

@app.route("/vid-from-link/<id>")
def videos_from_link(id: str) -> Tuple[List[Dict[str, Any]], int]:
    sub_dict = subscriptions.find_one({"_id": id})
    if sub_dict:
        return vid_dicts_from_tuple_list(sub_dict["videos"]), 200
    return [{'error': "Subscription %s not found"%id }], 404

@app.route("/sub-info/<id>")
def sub_dict(id: str) -> Tuple[Dict[str, Any], int]:
    sub_dict = subscriptions.find_one({"_id": id})
    if sub_dict:
        return sub_info_from_dict(sub_dict), 200
    return {'error': "Subscription %s not found"%id }, 404

@app.route("/subs-info")
def subs_info() -> List[Dict[str, Any]]:
    return [sub_info_from_dict(sub_dict) for sub_dict in subscriptions.find()]

@app.post("/add-sub/")
def add_sub() -> Tuple[Dict[str, Any], int]:
    try:
        sub_info = get_sub_info_from_yt_url(request.form["url"])
        time_between_fetches = int(request.form["time_between_fetches"])
    except:
        return {'error': 'Invalid data'}, 400
    sub = Subscription(
        _id=sub_info["id"],
        link=sub_info["link"],
        title=sub_info["title"],
        time_between_fetches=time_between_fetches,
    )
    try:
        sub.insert()
        return sub_info_from_dict(sub.asdict()), 201
    except DuplicateKeyError:
        return {'error': "Subscription %s already exists"%sub_info["id"] }, 409

@app.patch("/set-time-between-fetches/<id>")
def set_time_between_fetches(id: str) -> Tuple[Dict[str, Any], int]:
    try:
        time_between_fetches = int(request.form["time_between_fetches"])
    except:
        return {'error': 'Invalid data'}, 400
    result = subscriptions.update_one(
        {"_id": id},
        {"$set": {"time_between_fetches": time_between_fetches}}
    )
    if result.modified_count:
        return {
            "_id": id,
            "time_between_fetches": time_between_fetches,
        }, 200
    return {'error': "Subscription %s not found"%id }, 404

@app.delete("/delete-sub/<id>")
def delete_sub(id: str) -> Tuple[Dict[str, Any], int]:
    result = subscriptions.delete_one({"_id": id})
    if not result.deleted_count:
        return {'error': "Subscription %s not found"%id }, 404
    return { "_id": id, }, 200

@app.patch("/set-viewed/<id>")
def set_viewed(id:str) -> Tuple[Dict[str, Any], int]:
    viewed_time_str = request.form.get("viewed_time")
    if viewed_time_str:
        try:
            viewed_time = datetime.fromisoformat(viewed_time_str)
        except:
            return {'error': 'Invalid data'}, 400
    else:
        viewed_time = datetime.now(tz=UTC)
    result = subscriptions.update_one(
        {"_id": id},
        {"$set": {"last_viewed": viewed_time}}
    )
    if result.modified_count:
        return {
            "_id": id,
            "last_viewed": viewed_time,
        }, 200
    return {'error': "Subscription %s not found"%id }, 404

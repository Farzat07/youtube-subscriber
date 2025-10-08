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
        time_between_fetches=int(request.form["time_between_fetches"]),
    )
    sub.insert()
    return sub_info_from_dict(sub.asdict())

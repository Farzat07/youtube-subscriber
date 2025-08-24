from typing import Any, Dict, List
from components.database import subscriptions
from components.subscriptions.main import Subscription
from components.videos import VideoTuple
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/vid-from-link/<id>")
def videos_from_link(id: str) -> List[Dict[str, Any]]:
    sub = subscriptions.find_one({"_id": id})
    assert sub
    return [VideoTuple._make(vid)._asdict() for vid in sub["videos"]]

from typing import Any, Dict, List
from components.subscriptions.main import Subscription
from components.subscriptions.typing import SubsDict
from components.videos import VideoTuple

def vid_dicts_from_tuple_list(tuple_list: List[VideoTuple]) -> List[Dict[str, Any]]:
    return [VideoTuple._make(vid)._asdict() for vid in tuple_list]

def sub_info_from_dict(sub_dict: SubsDict) -> Dict[str, Any]:
    return {
        **sub_dict,
        "videos": len(sub_dict["videos"]),
        "new_vids": len(Subscription(**sub_dict).get_new_vids()),
    }

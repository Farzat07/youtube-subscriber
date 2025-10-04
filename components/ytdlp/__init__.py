from typing import Any, Dict
from json import dumps
from yt_dlp import YoutubeDL # type: ignore

def obtain_vid_info(url: str) -> Dict[str, Any]:
    ydl_opts = { "check_formats": False, }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return {"duration": info["duration"]}

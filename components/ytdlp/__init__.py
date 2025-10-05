from json import dumps
from sys import stderr
from typing import Any, Dict

from yt_dlp import YoutubeDL # type: ignore

def obtain_vid_info(url: str) -> Dict[str, Any]:
    ydl_opts = { "check_formats": False, } # We only want the durations.
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        return { "duration_string": info["duration_string"] }
    except Exception as e:
        print("Ran into an exception while fetching", url + ":", e, file=stderr)
        # This is a dummy project. If yt-dlp fails, repeatedly parsing YouTube
        # would only get us possibly blocked. Better return an empty string
        # instead.
        return { "duration_string": "" }

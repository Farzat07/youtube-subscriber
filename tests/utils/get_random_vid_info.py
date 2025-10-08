from hashlib import md5

def get_random_vid_duration(url: str) -> int:
    hash = md5(url.encode()).hexdigest()
    return int(hash[:4], 16)

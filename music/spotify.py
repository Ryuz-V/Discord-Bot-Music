import urllib.request
import re

def is_spotify_url(query: str) -> bool:
    return "open.spotify.com" in query or "spotify:" in query

def get_spotify_info(url: str) -> dict:
    try:
        if "track" not in url:
            raise ValueError("Only Spotify tracks are supported right now.")

        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read().decode('utf-8')

        title_match = re.search(r'<meta property="og:title" content="([^"]+)"', html)
        desc_match = re.search(r'<meta property="og:description" content="([^"]+)"', html)
        image_match = re.search(r'<meta property="og:image" content="([^"]+)"', html)
        duration_match = re.search(r'<meta name="music:duration" content="(\d+)"', html)

        title = title_match.group(1) if title_match else "Unknown Title"
        
        artist = "Unknown Artist"
        if desc_match:
            desc = desc_match.group(1)
            parts = desc.split(" · ")
            if len(parts) > 0:
                artist = parts[0]

        thumbnail = image_match.group(1) if image_match else None
        duration = int(duration_match.group(1)) if duration_match else 0
        
        return {
            "title": f"{title}",
            "author": artist,
            "duration": duration,
            "thumbnail": thumbnail,
            "url": url,
            "source": "spotify",
            "search_query": f"{title} {artist} audio"
        }
    except Exception as e:
        print(f"Spotify extraction error: {e}")
        return None

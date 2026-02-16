import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# 🔑 ganti CLIENT_ID dan CLIENT_SECRET kamu
sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id="CLIENT_ID_KAMU",
        client_secret="CLIENT_SECRET_KAMU"
    )
)

def is_spotify_url(query: str) -> bool:
    return "open.spotify.com" in query

def get_spotify_query(url: str) -> str:
    track = sp.track(url)
    title = track["name"]
    artist = track["artists"][0]["name"]
    return f"{title} {artist}"

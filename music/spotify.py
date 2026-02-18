import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# 🔑 ganti CLIENT_ID dan CLIENT_SECRET kamu
sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id="20e2bb9f1fdc4fca903840556e8c0a76",
        client_secret="22f3b14617054f59a3f3e5fa478d8bf8"
    )
)

def is_spotify_url(query: str) -> bool:
    return "open.spotify.com" in query

def get_spotify_query(url: str) -> str:
    track = sp.track(url)
    title = track["name"]
    artist = track["artists"][0]["name"]
    return f"{title} {artist}"

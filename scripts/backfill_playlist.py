"""One-off: add every song already in data/songs.json to your Spotify playlist.

  SPOTIFY_CLIENT_ID=... SPOTIFY_CLIENT_SECRET=... SPOTIFY_REFRESH_TOKEN=... \
  SPOTIFY_PLAYLIST_ID=... python scripts/backfill_playlist.py
"""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import update

ids = [s["id"] for s in json.loads(update.DATA.read_text())]
for i in range(0, len(ids), 100):
    ok = update.add_tracks_to_playlist(ids[i:i + 100])
    print(f"batch {i // 100 + 1}:", {True: "added", False: "FAILED", None: "secrets not set"}[ok])
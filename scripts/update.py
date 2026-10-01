"""Processes one song-suggestion issue and rewrites the README section.

Only open.spotify.com/track links are accepted. Every piece of text that ends up in
the README comes from the Spotify API (never from the issue), and is HTML-escaped.
"""
import base64
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "songs.json"
BANNED = ROOT / "data" / "banned.json"
README = ROOT / "README.md"
START, END = "<!--SONG:START-->", "<!--SONG:END-->"

# ---- settings -------------------------------------------------------------
HISTORY_SHOWN = 8          # rows in the "previously played" table
COOLDOWN_HOURS = 24        # one suggestion per user per this many hours
MIN_ACCOUNT_AGE_DAYS = 7   # reject brand new accounts (0 to disable)
BLOCK_EXPLICIT = True      # reject tracks Spotify flags as explicit
MAX_INPUT_CHARS = 4000
# ---------------------------------------------------------------------------

TRACK_RE = re.compile(
    r"https://open\.spotify\.com/(?:intl-[a-z]{2,3}/)?track/([A-Za-z0-9]{22})(?![A-Za-z0-9])"
)


class Reject(Exception):
    """A suggestion that is refused; the message is shown to the user."""


def http(url, data=None, headers=None, method=None):
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    req.add_header("User-Agent", "profile-song-game")
    with urllib.request.urlopen(req, timeout=20) as r:
        body = r.read()
    return json.loads(body) if body else {}


def _basic():
    pair = f"{os.environ['SPOTIFY_CLIENT_ID']}:{os.environ['SPOTIFY_CLIENT_SECRET']}"
    return "Basic " + base64.b64encode(pair.encode()).decode()


def _token(form):
    return http(
        "https://accounts.spotify.com/api/token",
        urllib.parse.urlencode(form).encode(),
        {"Authorization": _basic(), "Content-Type": "application/x-www-form-urlencoded"},
    )["access_token"]


def get_track(track_id):
    tok = _token({"grant_type": "client_credentials"})
    t = http(f"https://api.spotify.com/v1/tracks/{track_id}", headers={"Authorization": f"Bearer {tok}"})
    if t.get("type") != "track":
        raise Reject("That link is not a Spotify track.")
    images = sorted(t["album"].get("images", []), key=lambda i: abs((i.get("width") or 0) - 300))
    return {
        "id": t["id"],
        "title": t["name"],
        "artists": [a["name"] for a in t["artists"]],
        "album": t["album"]["name"],
        "image": images[0]["url"] if images else "",
        "url": t["external_urls"]["spotify"],
        "explicit": bool(t.get("explicit")),
    }


def account_age_days(login):
    try:
        u = http(
            f"https://api.github.com/users/{urllib.parse.quote(login)}",
            headers={"Authorization": "Bearer " + os.environ.get("GH_TOKEN", ""), "Accept": "application/vnd.github+json"},
        )
        created = datetime.fromisoformat(u["created_at"].replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - created).days
    except Exception:
        return None  # do not block on a lookup failure


def playlist_id():
    """Accepts a bare ID, a playlist URL (with or without ?si=...), or a spotify:playlist: URI."""
    raw = (os.environ.get("SPOTIFY_PLAYLIST_ID") or "").strip()
    m = re.search(r"playlist[/:]([A-Za-z0-9]{22})", raw) or re.match(r"([A-Za-z0-9]{22})(?:[?&#].*)?$", raw)
    return m.group(1) if m else None


def playlist_track_ids(pid, headers):
    """Return track IDs already in the playlist, using the current API first."""
    for path in ("items", "tracks"):
        found = set()
        offset = 0
        try:
            while True:
                page = http(
                    f"https://api.spotify.com/v1/playlists/{pid}/{path}?limit=100&offset={offset}",
                    headers=headers,
                )
                for entry in page.get("items", []):
                    track = entry.get("item") or entry.get("track") or entry
                    track_id = track.get("id") if isinstance(track, dict) else None
                    if track_id:
                        found.add(track_id)
                items = page.get("items", [])
                if not page.get("next") or not items:
                    return found
                offset += len(items)
        except urllib.error.HTTPError as e:
            if e.code not in (404, 405):
                raise
    return set()


def add_tracks_to_playlist(track_ids):
    """Optional: append to a real Spotify playlist. Returns True, False, or None (not configured).

    Skips tracks already present, then tries POST /items and falls back to POST /tracks
    if Spotify answers 404/405. Details go to the Action log only.
    """
    refresh, pid = os.environ.get("SPOTIFY_REFRESH_TOKEN"), playlist_id()
    if not os.environ.get("SPOTIFY_PLAYLIST_ID") or not refresh:
        return None
    if not pid:
        print("playlist add failed: SPOTIFY_PLAYLIST_ID is not a valid playlist id or link", file=sys.stderr)
        return False
    try:
        tok = _token({"grant_type": "refresh_token", "refresh_token": refresh})
    except Exception as e:
        print("playlist add failed: could not refresh token:", repr(e), file=sys.stderr)
        return False
    headers = {"Authorization": f"Bearer {tok}", "Content-Type": "application/json"}
    requested = list(dict.fromkeys(t for t in track_ids if t))
    if not requested:
        return True
    try:
        existing = playlist_track_ids(pid, headers)
    except Exception as e:
        print("playlist add failed: could not read existing items:", repr(e), file=sys.stderr)
        return False
    pending = [track_id for track_id in requested if track_id not in existing]
    if not pending:
        print("playlist already contains all requested tracks")
        return True

    for start in range(0, len(pending), 100):
        body = json.dumps({"uris": [f"spotify:track:{t}" for t in pending[start:start + 100]]}).encode()
        added = False
        for path in ("items", "tracks"):
            try:
                http(f"https://api.spotify.com/v1/playlists/{pid}/{path}", body, headers, "POST")
                added = True
                break
            except urllib.error.HTTPError as e:
                detail = e.read()[:300].decode("utf-8", "replace")
                print(f"playlist add via /{path} failed: HTTP {e.code} {detail}", file=sys.stderr)
                if e.code not in (404, 405):
                    return False
            except Exception as e:
                print(f"playlist add via /{path} failed: {e!r}", file=sys.stderr)
                return False
        if not added:
            return False
    return True


def add_to_playlist(track_id):
    return add_tracks_to_playlist([track_id])


def esc(s):
    return html.escape(str(s), quote=True).replace("|", "&#124;")


def render(songs):
    playlist = playlist_id()
    if not songs:
        return "No song yet. Be the first to suggest one."
    cur = songs[-1]
    when = cur["at"][:10]
    out = [
        "<table><tr>",
        f'<td><a href="{esc(cur["url"])}"><img src="{esc(cur["image"])}" width="200" alt="Album art for {esc(cur["album"])}"></a></td>',
        '<td valign="top">',
        "<sub>NOW PLAYING</sub><br>",
        f'<h3><a href="{esc(cur["url"])}">{esc(cur["title"])}</a></h3>',
        f'{esc(", ".join(cur["artists"]))}<br>',
        f'<sub>{esc(cur["album"])}</sub><br><br>',
        f'suggested by <a href="https://github.com/{esc(cur["by"])}"><b>@{esc(cur["by"])}</b></a> on {esc(when)}<br>',
        f'<sub>song #{len(songs)} in the chain</sub>',
        "</td></tr></table>",
    ]
    prev = list(reversed(songs[:-1]))[:HISTORY_SHOWN]
    if prev:
        out += ["", "<b>Previously played</b>", "", "<table>"]
        for s in prev:
            out.append(
                "<tr>"
                f'<td><a href="{esc(s["url"])}"><img src="{esc(s["image"])}" width="48" alt=""></a></td>'
                f'<td><a href="{esc(s["url"])}">{esc(s["title"])}</a><br><sub>{esc(", ".join(s["artists"]))}</sub></td>'
                f'<td><sub>by <a href="https://github.com/{esc(s["by"])}">@{esc(s["by"])}</a></sub></td>'
                "</tr>"
            )
        out.append("</table>")
    if playlist:
        out += ["", f'<a href="https://open.spotify.com/playlist/{esc(playlist)}">Listen to the full playlist ({len(songs)} songs and counting)</a>']
    return "\n".join(out)


def write_readme(songs):
    text = README.read_text()
    if START not in text or END not in text:
        raise RuntimeError("README markers missing")
    block = f"{START}\n{render(songs)}\n{END}"
    README.write_text(re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block, text, flags=re.S))


def process(title, body, user, owner=None, now=None):
    now = now or datetime.now(timezone.utc)
    text = f"{title or ''}\n{body or ''}"[:MAX_INPUT_CHARS]
    m = TRACK_RE.search(text)
    if not m:
        raise Reject(
            "I could not find a Spotify track link. Paste a link like "
            "`https://open.spotify.com/track/...` (use Share > Copy Song Link in Spotify). "
            "Album, playlist and spotify.link short URLs are not supported."
        )
    track_id = m.group(1)
    is_owner = owner is not None and user.lower() == owner.lower()

    banned = {u.lower() for u in json.loads(BANNED.read_text()).get("users", [])} if BANNED.exists() else set()
    if user.lower() in banned:
        raise Reject("You are not able to suggest songs here.")

    songs = json.loads(DATA.read_text()) if DATA.exists() else []

    if not is_owner:
        if MIN_ACCOUNT_AGE_DAYS:
            age = account_age_days(user)
            if age is not None and age < MIN_ACCOUNT_AGE_DAYS:
                raise Reject(f"Accounts need to be at least {MIN_ACCOUNT_AGE_DAYS} days old to suggest songs.")
        cutoff = now - timedelta(hours=COOLDOWN_HOURS)
        for s in reversed(songs):
            if s["by"].lower() == user.lower() and datetime.fromisoformat(s["at"]) > cutoff:
                raise Reject(f"One suggestion per {COOLDOWN_HOURS} hours. Come back later.")
    if any(s["id"] == track_id for s in songs):
        raise Reject("That song has already been played in this chain. Try another one.")

    track = get_track(track_id)
    if BLOCK_EXPLICIT and track.pop("explicit") and not is_owner:
        raise Reject("That track is marked explicit, so it cannot go on the profile. Try a clean version or another song.")
    track.pop("explicit", None)

    track.update(by=user, at=now.isoformat(timespec="seconds"))
    songs.append(track)
    DATA.write_text(json.dumps(songs, indent=2) + "\n")
    write_readme(songs)

    added = add_tracks_to_playlist([s["id"] for s in songs])
    msg = f"Added **{esc(track['title'])}** by {esc(', '.join(track['artists']))}. It is now playing on the profile README."
    if added is True:
        msg += " The Spotify playlist is synchronized."
    elif added is False:
        msg += " The playlist add failed, so check the Action log. The song is still on the README."
    return msg


def main():
    out = os.environ.get("GITHUB_OUTPUT")
    reply = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "reply.md"
    try:
        msg = process(
            os.environ.get("ISSUE_TITLE", ""),
            os.environ.get("ISSUE_BODY", ""),
            os.environ["ISSUE_USER"],
            os.environ.get("GITHUB_REPOSITORY_OWNER"),
        )
        result = "ok"
    except Reject as r:
        msg, result = str(r), "rejected"
    except Exception as e:  # network errors, bad credentials, etc.
        print("error:", repr(e), file=sys.stderr)
        msg, result = "Something went wrong on my side while processing that. The maintainer has been notified by the failed run.", "error"
    reply.write_text(msg + "\n")
    if out:
        with open(out, "a") as f:
            f.write(f"result={result}\nreply_file={reply}\n")
    print(result, "-", msg)
    return 1 if result == "error" else 0


if __name__ == "__main__":
    sys.exit(main())
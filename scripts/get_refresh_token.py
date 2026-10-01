"""One-time helper: gets a Spotify refresh token so the Action can add songs to your playlist.

  SPOTIFY_CLIENT_ID=... SPOTIFY_CLIENT_SECRET=... python scripts/get_refresh_token.py

The redirect URI http://127.0.0.1:8888/callback must be added to your Spotify app settings.
"""
import base64, json, os, secrets, urllib.parse, urllib.request, webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

CID, SEC = os.environ["SPOTIFY_CLIENT_ID"], os.environ["SPOTIFY_CLIENT_SECRET"]
REDIRECT = "http://127.0.0.1:8888/callback"
STATE = secrets.token_urlsafe(8)
got = {}


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if q.get("state", [None])[0] == STATE and "code" in q:
            got["code"] = q["code"][0]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Done. You can close this tab.")

    def log_message(self, *a):
        pass


url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(
    {"client_id": CID, "response_type": "code", "redirect_uri": REDIRECT,
     "scope": "playlist-modify-public playlist-modify-private", "state": STATE}
)
print("Opening browser. If nothing opens, visit:\n" + url)
webbrowser.open(url)
srv = HTTPServer(("127.0.0.1", 8888), H)
while "code" not in got:
    srv.handle_request()

req = urllib.request.Request(
    "https://accounts.spotify.com/api/token",
    urllib.parse.urlencode({"grant_type": "authorization_code", "code": got["code"], "redirect_uri": REDIRECT}).encode(),
    {"Authorization": "Basic " + base64.b64encode(f"{CID}:{SEC}".encode()).decode(),
     "Content-Type": "application/x-www-form-urlencoded"},
)
print("\nSPOTIFY_REFRESH_TOKEN =", json.load(urllib.request.urlopen(req))["refresh_token"])

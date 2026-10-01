# Setup

This repo must be named `blazewexe/blazewexe` (same as the username) and be public. Issues must be enabled, which is the default for new repos.

## 1. Spotify app (required)

1. Go to https://developer.spotify.com/dashboard and create an app. Any name works.
2. Add the redirect URI `http://127.0.0.1:8888/callback` (only needed for step 3).
3. Copy the Client ID and Client Secret.
4. In the GitHub repo go to Settings, Secrets and variables, Actions, and add:
   - `SPOTIFY_CLIENT_ID`
   - `SPOTIFY_CLIENT_SECRET`

This is enough for the game to work. Looking up a track needs no user login (client credentials flow).

## 2. Repo settings

Settings, Actions, General, Workflow permissions: set to "Read and write permissions". The workflow also declares its own permissions block, but the repo setting must not forbid it.

## 3. Real Spotify playlist (optional, makes it a true infinite playlist)

1. In Spotify create a playlist, make it public, and copy the ID from its link (`open.spotify.com/playlist/<ID>`).
2. Locally run:

       SPOTIFY_CLIENT_ID=... SPOTIFY_CLIENT_SECRET=... python scripts/get_refresh_token.py

   Approve in the browser and copy the printed refresh token.
3. Add secrets `SPOTIFY_REFRESH_TOKEN` and `SPOTIFY_PLAYLIST_ID`.

Notes:
- The playlist must be owned by the account that authorized the token.
- Spotify development-mode apps require the app owner to have Premium, and refresh tokens now expire after about six months. If songs stop reaching the playlist, rerun the helper and update the secret. The README game itself keeps working either way.
- The add call uses `POST /playlists/{id}/items`, the endpoint that replaced `/tracks` in Spotify's 2026 API changes.

## 4. Customize

- Header text, BPM and colors: edit `scripts/make_header.py`, run `python scripts/make_header.py`, commit `assets/header.svg`.
- Rules: constants at the top of `scripts/update.py` (cooldown, explicit filter, minimum account age, rows shown).
- Ban someone: add their username to `data/banned.json`.
- Remove a song: delete its entry from `data/songs.json`, then run `python -c "import sys; sys.path.insert(0,'scripts'); import update, json; update.write_readme(json.load(open('data/songs.json')))"` and commit.

## How it works

1. The issue form collects a Spotify link.
2. `song-game.yml` runs `scripts/update.py` with the issue text passed only through environment variables.
3. The script matches a strict `open.spotify.com/track/<22 chars>` pattern, checks ban list, account age, cooldown and duplicates, then fetches title, artists, album and cover art from Spotify.
4. Only Spotify-provided, HTML-escaped values are written to `data/songs.json` and to the README block between the `SONG:START` and `SONG:END` markers.
5. The workflow commits, comments on the issue and closes it. A concurrency group keeps simultaneous suggestions from colliding.

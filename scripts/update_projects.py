"""Refresh the profile README with the three most recently pushed public repos."""
import html
import json
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
START, END = "<!--PROJECTS:START-->", "<!--PROJECTS:END-->"
OWNER = "blazewexe"
PROFILE_REPO = f"{OWNER}/{OWNER}"
DESCRIPTIONS = {
    "openpass": "Event management and ticketing platform.",
    "Wex-To-Do-List": "A lightweight task list with filters, sorting, and local persistence.",
    "yt-music-rpc": "YouTube Music Discord Rich Presence and Last.fm scrobbling.",
}


def clean(value):
    """Keep API text on one safe Markdown line."""
    value = re.sub(r"\s+", " ", str(value or "")).strip()
    return html.escape(value, quote=False).replace("|", "&#124;")


def repositories():
    url = f"https://api.github.com/users/{OWNER}/repos?type=owner&sort=pushed&per_page=100"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "blazewexe-profile-readme",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.load(response)
    if not isinstance(data, list):
        raise ValueError("GitHub did not return a repository list")
    return [
        repo for repo in data
        if not repo.get("private")
        and not repo.get("archived")
        and repo.get("full_name", "").lower() != PROFILE_REPO.lower()
    ][:3]


def render(repos):
    if not repos:
        return "No public projects found yet."
    rows = []
    for repo in repos:
        name = clean(repo.get("name", "Project"))
        slug = urllib.parse.quote(repo.get("name", ""), safe="-_.")
        link = f"https://github.com/{OWNER}/{slug}"
        project = f"**[{name}]({link})**"
        if repo.get("fork"):
            project += " *(fork)*"
        homepage = repo.get("homepage") or ""
        if homepage.startswith(("https://", "http://")):
            homepage = homepage.replace(" ", "%20").replace("(", "%28").replace(")", "%29")
            project += f" · [Live demo]({homepage})"
        description = clean(repo.get("description") or DESCRIPTIONS.get(repo.get("name")) or "")
        rows.append(f"- {project} — {description}" if description else f"- {project}")
    return "\n".join(rows)


def main():
    text = README.read_text(encoding="utf-8")
    if START not in text or END not in text:
        raise RuntimeError("Project markers missing from README")
    block = f"{START}\n{render(repositories())}\n{END}"
    updated = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block, text, flags=re.S)
    if updated != text:
        README.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    main()

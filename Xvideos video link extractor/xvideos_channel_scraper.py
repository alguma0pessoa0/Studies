import requests
import sys
import re
import time
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7",
    "Referer": "https://www.xvideos.com/",
}

session = requests.Session()
session.headers.update(HEADERS)


def extract_slug(url: str) -> str:
    url = url.strip().rstrip("/")
    patterns = [
        r"xvideos\.com/channels/([^/?]+)",
        r"xvideos\.com/profiles/([^/?]+)",
        r"xvideos\.com/([^/?]+)",
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    raise ValueError(f"Could not extract channel slug from URL: {url}")


def detect_type(slug: str) -> str:
    r = session.get(f"https://www.xvideos.com/{slug}", timeout=15)
    if r.status_code == 404:
        raise SystemExit(f"Error: Page not found for slug '{slug}'")
    if f"/channels/{slug}" in r.text or f'channels/{slug}' in r.text:
        return "channel"
    return "profile"


def fetch_channel_videos(slug: str) -> list[str]:
    base_url = f"https://www.xvideos.com/channels/{slug}/videos/best"
    urls = []
    page = 0

    print(f"Scraping channel: {slug}")
    while True:
        page_url = f"{base_url}/{page}"
        print(f"  Page {page}...", end=" ", flush=True)

        r = session.get(page_url, timeout=15)
        if r.status_code != 200:
            print(f"HTTP {r.status_code} - stopping.")
            break

        try:
            data = r.json()
        except (json.JSONDecodeError, requests.exceptions.JSONDecodeError):
            print("Non-JSON response. Stopping.")
            break

        videos = data.get("videos", [])
        if not videos:
            print("No videos found.")
            break

        for v in videos:
            vid_url = f"https://www.xvideos.com{video_href(v)}"
            urls.append(vid_url)

        total = data.get("nb_videos", 0)
        shown = len(urls)
        print(f"{len(videos)} videos (total: {shown}/{total})")

        if shown >= total:
            break

        page += 1
        time.sleep(0.3)

    return urls


def video_href(v: dict) -> str:
    eid = v.get("eid")
    if eid:
        return f"/video.{eid}/_"
    for key in ("u", "url", "video_url", "link"):
        val = v.get(key)
        if val:
            return val
    for key in ("k", "id", "video_id"):
        val = v.get(key)
        if val:
            return f"/video{val}/_"
    raise ValueError(f"Could not extract video href: {v}")


def fetch_profile_videos(slug: str) -> list[str]:
    base_url = f"https://www.xvideos.com/profiles/{slug}/videos/best"
    urls = []
    page = 0

    print(f"Scraping profile: {slug}")
    while True:
        page_url = f"{base_url}/{page}"
        print(f"  Page {page}...", end=" ", flush=True)

        r = session.get(page_url, timeout=15)
        if r.status_code != 200:
            print(f"HTTP {r.status_code} - stopping.")
            break

        try:
            data = r.json()
        except (json.JSONDecodeError, requests.exceptions.JSONDecodeError):
            print("Non-JSON response. Stopping.")
            break

        videos = data.get("videos", [])
        if not videos:
            print("No videos found.")
            break

        for v in videos:
            vid_url = f"https://www.xvideos.com{video_href(v)}"
            urls.append(vid_url)

        total = data.get("nb_videos", 0)
        shown = len(urls)
        print(f"{len(videos)} videos (total: {shown}/{total})")

        if shown >= total:
            break

        page += 1
        time.sleep(0.3)

    return urls


def save_links(links: list[str], filename: str = "videos.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        for link in links:
            f.write(link + "\n")
    print(f"\n{len(links)} links saved in {filename}")


def main():
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("XVideos channel URL: ").strip()

    if not url:
        print("No URL provided.")
        sys.exit(1)

    slug = extract_slug(url)
    print(f"Extracted slug: {slug}")

    links = fetch_channel_videos(slug)
    if not links:
        links = fetch_profile_videos(slug)

    if links:
        save_links(links)
    else:
        print("No videos found.")


if __name__ == "__main__":
    main()

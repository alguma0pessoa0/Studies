import sys
import re
import time
import random
from urllib.parse import urlparse, parse_qs, urljoin
from pathlib import Path

from bs4 import BeautifulSoup
from curl_cffi import requests


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7",
    "Referer": "https://www.pornhub.com/",
}

session = requests.Session()
session.headers.update(HEADERS)


def extract_channel_name(url: str) -> str:
    url = url.strip().rstrip("/")
    m = re.search(r"pornhub\.com/channels/([^/?]+)", url, re.IGNORECASE)
    if not m:
        raise ValueError(
            "Invalid URL. Use: "
            "https://www.pornhub.com/channels/CHANNEL_NAME"
        )
    return m.group(1).lower()


def extract_viewkeys(html: str) -> set[str]:
    soup = BeautifulSoup(html, "html.parser")
    keys: set[str] = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        parsed = urlparse(href)
        qs = parse_qs(parsed.query)
        vk = qs.get("viewkey", [None])[0]
        if vk and re.match(r"^[a-f0-9]{8,}$", vk):
            keys.add(vk)
    return keys


def build_url(vk: str) -> str:
    return f"https://www.pornhub.com/view_video.php?viewkey={vk}"


def get_next_page_url(soup: BeautifulSoup, base_url: str) -> str | None:
    next_link = soup.find("a", class_="page_next")
    if next_link and next_link.get("href"):
        return urljoin(base_url, next_link["href"])

    next_link = soup.select_one("li.page_next a")
    if next_link and next_link.get("href"):
        return urljoin(base_url, next_link["href"])

    pagination = soup.find("div", class_="pagination")
    if pagination:
        current = pagination.find("a", class_="current_page")
        if current:
            parent = current.parent
            sibling = parent.find_next_sibling("li") if parent else None
            if sibling:
                link = sibling.find("a")
                if link and link.get("href"):
                    return urljoin(base_url, link["href"])
        links_after = current.find_all_next("a") if current else None
        if links_after:
            for la in links_after:
                if la.get("href") and "page=" in la["href"]:
                    return urljoin(base_url, la["href"])

    return None


def collect_channel_urls(channel_url: str, delay: float = 3.0) -> list[str]:
    channel_name = extract_channel_name(channel_url)
    all_keys: set[str] = set()
    page = 1
    current_url = channel_url

    print(f"Collecting videos from channel: {channel_name}")

    while current_url:
        print(f"  Page {page}...", end=" ", flush=True)

        try:
            r = session.get(
                current_url,
                impersonate="chrome",
                timeout=30,
            )
        except Exception as e:
            print(f"Request error: {e}")
            break

        if r.status_code != 200:
            print(f"HTTP {r.status_code} - stopping.")
            break

        viewkeys = extract_viewkeys(r.text)
        print(f"{len(viewkeys)} videos "
              f"(total so far: {len(all_keys) + len(viewkeys)})",
              flush=True)

        all_keys |= viewkeys

        soup = BeautifulSoup(r.text, "html.parser")
        next_url = get_next_page_url(soup, current_url)

        if not next_url or next_url == current_url:
            print("End of catalog.")
            break

        current_url = next_url
        wait_time = delay + random.uniform(0.5, 2.0)
        time.sleep(wait_time)
        page += 1

    urls = sorted(build_url(vk) for vk in all_keys)
    return urls


def save_links(links: list[str], channel_name: str):
    file_path = Path(f"{channel_name}_videos.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        for link in links:
            f.write(link + "\n")
    print(f"\n{len(links)} links saved in {file_path}")


def main():
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Pornhub channel URL: ").strip()

    if not url:
        print("No URL provided.")
        sys.exit(1)

    if not url.startswith("http"):
        url = "https://" + url

    channel_name = extract_channel_name(url)
    print(f"Channel: {channel_name}")

    links = collect_channel_urls(url)

    if links:
        save_links(links, channel_name)
    else:
        print("No videos found.")


if __name__ == "__main__":
    main()

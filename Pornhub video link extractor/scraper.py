import sys
import re
import time
import random
from urllib.parse import urlparse, parse_qs
from pathlib import Path

from bs4 import BeautifulSoup
from curl_cffi import requests
from colorama import Fore, Back, Style, init

init(autoreset=True)


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
    m = re.search(r"pornhub\.com/(?:channels|model)/([^/?]+)", url, re.IGNORECASE)
    if not m:
        raise ValueError(
            f"{Fore.RED}Invalid URL.{Fore.RESET} Use: "
            f"{Fore.CYAN}https://pt.pornhub.com/model/MODEL_NAME/videos{Fore.RESET}"
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


def make_page_url(base_url: str, page: int) -> str:
    base_url = base_url.rstrip("/")
    if page <= 1:
        return base_url
    return f"{base_url}?page={page}"


def collect_channel_urls(channel_url: str, delay: float = 3.0) -> list[str]:
    channel_name = extract_channel_name(channel_url)
    all_keys: set[str] = set()
    page = 1

    base_url = channel_url.rstrip("/")
    if not base_url.endswith("/videos"):
        base_url = base_url + "/videos"

    print(f"\n{Fore.MAGENTA}{Style.BRIGHT}── {Fore.CYAN}Collecting videos from channel: {Fore.YELLOW}{channel_name}{Fore.MAGENTA} ──{Style.RESET_ALL}\n")

    while True:
        current_url = make_page_url(base_url, page)
        print(f"  {Fore.BLUE}Page {Fore.WHITE}{page}{Fore.BLUE}...{Style.RESET_ALL}", end=" ", flush=True)

        try:
            r = session.get(
                current_url,
                impersonate="chrome",
                timeout=30,
            )
        except Exception as e:
            print(f"{Fore.RED}✖ Request error: {e}{Style.RESET_ALL}")
            break

        if r.status_code == 404:
            print(f"{Fore.YELLOW}■ End of catalog (404).{Style.RESET_ALL}")
            break

        if r.status_code != 200:
            print(f"{Fore.RED}■ HTTP {r.status_code} - stopping.{Style.RESET_ALL}")
            break

        viewkeys = extract_viewkeys(r.text)
        print(f"{Fore.GREEN}{len(viewkeys)} videos "
              f"{Fore.WHITE}(total so far: {Fore.CYAN}{len(all_keys) + len(viewkeys)}{Fore.WHITE}){Style.RESET_ALL}",
              flush=True)

        if not viewkeys:
            print(f"{Fore.YELLOW}■ No videos found on this page - stopping.{Style.RESET_ALL}")
            break

        all_keys |= viewkeys

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
    print(f"\n{Fore.GREEN}{Style.BRIGHT}✔ {len(links)} links saved in {Fore.CYAN}{file_path}{Style.RESET_ALL}")


def main():
    print(f"{Fore.MAGENTA}{Style.BRIGHT}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{Style.BRIGHT}  Pornhub Video Link Extractor{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}{'='*60}{Style.RESET_ALL}\n")

    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input(f"{Fore.CYAN}Pornhub channel URL{Fore.WHITE}:{Style.RESET_ALL} ").strip()

    if not url:
        print(f"{Fore.RED}No URL provided.{Style.RESET_ALL}")
        sys.exit(1)

    if not url.startswith("http"):
        url = "https://" + url

    channel_name = extract_channel_name(url)
    print(f"{Fore.CYAN}Channel{Fore.WHITE}: {Fore.YELLOW}{channel_name}{Style.RESET_ALL}")

    links = collect_channel_urls(url)

    if links:
        save_links(links, channel_name)
    else:
        print(f"{Fore.RED}No videos found.{Style.RESET_ALL}")


if __name__ == "__main__":
    main()

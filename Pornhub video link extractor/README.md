# Pornhub Channel Scraper

Extracts all video URLs from a Pornhub channel and saves them to a `.txt` file.

## Requirements

- Python 3.10+
- `pip`

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python scraper.py
```

Enter the channel/model URL when prompted. Example:

```
Pornhub channel URL: https://pt.pornhub.com/model/babyxscarlett/videos
```

Or pass the URL as an argument:

```bash
python scraper.py "https://pt.pornhub.com/model/babyxscarlett/videos"
```

The program creates a `{channel-name}_videos.txt` file with the URLs, one per line.

## How it works

1. Uses `curl_cffi` with Chrome impersonation to bypass Cloudflare
2. Navigates pages using `?page=N` (page 1 has no parameter)
3. Stops when the server returns 404 (last page reached)
4. Extracts the `viewkey` from each video
5. Builds the full URL and saves to a `.txt` file

## Notes

- Channels with thousands of videos may take a few minutes
- Respect the site's terms of service
- Use sparingly to avoid overloading the server

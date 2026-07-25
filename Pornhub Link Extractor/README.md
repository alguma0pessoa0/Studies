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

Enter the channel URL when prompted. Example:

```
Pornhub channel URL: https://www.pornhub.com/channels/channel-name
```

Or pass the URL as an argument:

```bash
python scraper.py "https://www.pornhub.com/channels/channel-name"
```

The program creates a `{channel-name}_videos.txt` file with the URLs, one per line.

## How it works

1. Uses `curl_cffi` with Chrome impersonation to bypass Cloudflare
2. Navigates through all pages of the channel catalog
3. Extracts the `viewkey` from each video
4. Builds the full URL and saves to a `.txt` file

## Notes

- Channels with thousands of videos may take a few minutes
- Respect the site's terms of service
- Use sparingly to avoid overloading the server
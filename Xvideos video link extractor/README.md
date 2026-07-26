# XVideos Video Link Extractor

Extracts video links from XVideos channels and profiles.

## Usage

```bash
python xvideos_channel_scraper.py "<channel_url>"
```

If no link is passed as an argument, the program will prompt for the channel URL.

## Features

- Extracts the slug from the provided URL
- Automatically detects the type (channel or profile)
- Browses all video pages (sorted by popularity)
- Saves the extracted links to `videos.txt`

## Input format

- `https://www.xvideos.com/channels/foo`
- `https://www.xvideos.com/profiles/bar`
- `https://www.xvideos.com/baz`

## Dependencies

- [Python](https://www.python.org/) >= 3.8
- [requests](https://pypi.org/project/requests/)

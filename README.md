# family-tv

One combined TV playlist, rebuilt automatically every day.

A GitHub Action merges several category playlists from [iptv-org](https://github.com/iptv-org/iptv) (sports, movies, kids, entertainment, comedy, family and general) into a single `.m3u` file, removes channels that appear in more than one category, and publishes it here. About 5,600 channels.

## Use it

Add this URL to any player that supports M3U playlists (VLC, TiviMate, IPTV Smarters, Kodi, Jellyfin, Plex with an IPTV plugin and so on):

```
https://raw.githubusercontent.com/TheDarkOne26/family-tv/main/family_safe.m3u
```

Use the URL rather than a downloaded copy, so your player picks up each day's update. Most players only re-download a playlist on a schedule (often every 24 hours or more); look for a "refresh playlist" or "update interval" option if it seems out of date.

> **Note:** despite the file name, the playlist is not filtered for content. It includes everything iptv-org lists in those categories.

## How it works

| File | What it does |
|---|---|
| `iptv_scraper.py` | Downloads each category playlist, removes duplicate channels and writes `family_safe.m3u`. If a source fails, it keeps the previous playlist instead of publishing a broken one. |
| `.github/workflows/main.yml` | Runs the script daily and commits the playlist only when it actually changed. Can also be started from the **Actions** tab with **Run workflow**. |

To build it yourself: `python iptv_scraper.py` (Python 3, no extra packages).

## Disclaimer

This repo hosts no video. It only collects links that iptv-org publishes from publicly available sources. Whether a channel works depends on the broadcaster; some streams go offline or are blocked in some countries. Questions about a specific channel belong with [iptv-org](https://github.com/iptv-org/iptv).

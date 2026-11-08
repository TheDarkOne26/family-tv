# family-tv

One combined TV playlist, rebuilt automatically every day.

A GitHub Action merges several category playlists from [iptv-org](https://github.com/iptv-org/iptv) (sports, movies, kids, entertainment, comedy, family and general) into a single `.m3u` file and publishes it here. It keeps **English-language channels only**, drops channels iptv-org marks as geo-blocked or not 24/7 (they usually won't play), removes duplicates, and tests every stream so channels whose stream is gone are left out. About 1,150 channels.

## Use it

Add this URL to any player that supports M3U playlists (VLC, TiviMate, IPTV Smarters, Kodi, Jellyfin, Plex with an IPTV plugin and so on):

```
https://raw.githubusercontent.com/TheDarkOne26/family-tv/main/family_safe.m3u
```

Use the URL rather than a downloaded copy, so your player picks up each day's update. Most players only re-download a playlist on a schedule (often every 24 hours or more); look for a "refresh playlist" or "update interval" option if it seems out of date.

> **Note:** despite the file name, the playlist is not filtered for content. It includes everything iptv-org lists in those categories.

## Jellyfin

1. **Dashboard → Live TV → Tuner Devices → +** (the exact menu names vary a little between Jellyfin versions).
2. Tuner type **M3U Tuner**, file or URL: the playlist URL above. Save.
3. Open **Live TV** in Jellyfin and the channels appear, grouped by category.

Jellyfin re-reads the playlist when its **Refresh Guide** scheduled task runs (daily by default), so new and removed channels show up on their own. Run it from **Dashboard → Scheduled Tasks** to update right away.

The playlist has no program guide, so channels show without schedules. If you want one, add an XMLTV guide source under **Live TV → TV Guide Data Providers**; the `tvg-id` values in the playlist match iptv-org's guide IDs.

## Change what's included

Edit the settings at the top of `iptv_scraper.py`:

- `LANGUAGES`: language codes to keep, e.g. `["eng", "spa"]`. Use `[]` for every language.
- `SOURCE_URLS`: which iptv-org categories to merge.
- `SKIP_LABELS`: delete an entry to keep geo-blocked or part-time channels.
- `CHECK_STREAMS`: set to `False` to skip the daily stream test.

## Dead streams

Each run fetches every stream the way a player does and leaves out channels whose stream is clearly gone: removed (404 or 410), a server that no longer exists or refuses connections, a link that leads to a web page, or an empty playlist. A failing stream is retried once before it's dropped, and dropped channels come back on their own if the stream returns.

Channels that are only blocked (403), hit a server error or time out are kept, because some broadcasters block GitHub's servers but work fine at home. So some channels in the list may still not play for you. If more than a third of streams fail in one run, the script assumes the problem is on GitHub's side and drops nothing.

## How it works

| File | What it does |
|---|---|
| `iptv_scraper.py` | Downloads each category playlist, keeps the chosen languages, removes duplicate, unreliable and dead channels and writes `family_safe.m3u`. If a source fails, it keeps the previous playlist instead of publishing a broken one. |
| `.github/workflows/main.yml` | Runs the script daily and commits the playlist only when it actually changed. Can also be started from the **Actions** tab with **Run workflow**. |

To build it yourself: `python iptv_scraper.py` (Python 3.9+, no extra packages). The stream test takes a couple of minutes.

## Disclaimer

This repo hosts no video. It only collects links that iptv-org publishes from publicly available sources. Whether a channel works depends on the broadcaster; some streams go offline or are blocked in some countries. Questions about a specific channel belong with [iptv-org](https://github.com/iptv-org/iptv).

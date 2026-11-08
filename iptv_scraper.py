"""Builds family_safe.m3u by merging several iptv-org category playlists.

Only channels in the languages listed in LANGUAGES are kept, and channels
iptv-org marks as geo-blocked or not 24/7 are dropped, since those usually
fail to play. Channels that appear in more than one category are kept only
once. If any source fails to download, the script exits with an error and
leaves the existing playlist untouched, so a bad day never publishes a
half-empty list.
"""
import os
import sys
import urllib.request

OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "family_safe.m3u")

SOURCE_URLS = [
    "https://iptv-org.github.io/iptv/categories/sports.m3u",
    "https://iptv-org.github.io/iptv/categories/movies.m3u",
    "https://iptv-org.github.io/iptv/categories/kids.m3u",
    "https://iptv-org.github.io/iptv/categories/entertainment.m3u",
    "https://iptv-org.github.io/iptv/categories/comedy.m3u",
    "https://iptv-org.github.io/iptv/categories/family.m3u",
    "https://iptv-org.github.io/iptv/categories/general.m3u",
]

# ISO 639-3 language codes to keep, e.g. ["eng", "spa"]. Empty list keeps every language.
LANGUAGES = ["eng"]

# Channels whose name carries one of these iptv-org labels are dropped.
SKIP_LABELS = ["[Geo-blocked]", "[Not 24/7]"]

# A real playlist has hundreds of channels; far fewer means a source broke.
MIN_CHANNELS = 300


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "family-tv-playlist-builder"})
    with urllib.request.urlopen(req, timeout=60) as response:
        return response.read().decode("utf-8")


def parse_channels(text):
    """Yields (lines, stream_url) for each channel: its #EXTINF line, any
    option lines such as #EXTVLCOPT, and the stream URL that ends it."""
    block = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#EXTM3U"):
            continue
        if line.startswith("#EXTINF"):
            block = [line]
        elif line.startswith("#"):
            if block:
                block.append(line)
        elif block:
            block.append(line)
            yield block, line
            block = []


def fetch_or_exit(url):
    print(f"Fetching {url}")
    try:
        return fetch(url)
    except Exception as error:
        sys.exit(f"Failed to fetch {url}: {error}. Keeping the existing playlist.")


def allowed_streams():
    """Stream URLs of every channel in the wanted languages, or None for no filter.
    iptv-org publishes one playlist per language; a channel is kept if its
    stream appears in one of those."""
    if not LANGUAGES:
        return None
    allowed = set()
    for code in LANGUAGES:
        text = fetch_or_exit(f"https://iptv-org.github.io/iptv/languages/{code}.m3u")
        allowed.update(stream_url for _, stream_url in parse_channels(text))
    return allowed


def build_playlist():
    allowed = allowed_streams()
    seen_urls = set()
    output = ["#EXTM3U"]
    for url in SOURCE_URLS:
        text = fetch_or_exit(url)
        for lines, stream_url in parse_channels(text):
            if stream_url in seen_urls:
                continue
            if allowed is not None and stream_url not in allowed:
                continue
            if any(label in lines[0] for label in SKIP_LABELS):
                continue
            seen_urls.add(stream_url)
            output.extend(lines)

    count = len(seen_urls)
    if count < MIN_CHANNELS:
        sys.exit(f"Only {count} channels found, expected at least {MIN_CHANNELS}. Keeping the existing playlist.")

    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(output) + "\n")
    print(f"Wrote {count} channels to {OUTPUT_FILE}")


if __name__ == "__main__":
    build_playlist()

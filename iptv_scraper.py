"""Builds family_safe.m3u by merging several iptv-org category playlists.

Only channels in the languages listed in LANGUAGES are kept, and channels
iptv-org marks as geo-blocked or not 24/7 are dropped, since those usually
fail to play. Channels that appear in more than one category are kept only
once. Every remaining stream is then tested, and channels whose stream is
clearly gone are left out. If any source fails to download, the script exits
with an error and leaves the existing playlist untouched, so a bad day never
publishes a half-empty list.
"""
import concurrent.futures
import os
import socket
import sys
import urllib.error
import urllib.parse
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

# Test each stream and drop the ones that are clearly gone. Set to False to skip.
CHECK_STREAMS = True

# Streams are fetched the way players like Jellyfin and VLC fetch them.
PLAYER_USER_AGENT = "VLC/3.0.20 LibVLC/3.0.20"

# Only these failures count as dead. A block (403), a server error or a timeout
# keeps the channel: some broadcasters block GitHub's servers but work at home.
DEAD_HTTP_CODES = {404, 410}

# If more than this share of streams looks dead, the check itself is probably
# broken (for example a network problem on GitHub's side), so nothing is dropped.
MAX_DEAD_SHARE = 0.35


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


def player_headers(lines):
    """Request headers a player would send, including any #EXTVLCOPT referrer or user agent."""
    headers = {"User-Agent": PLAYER_USER_AGENT}
    for line in lines:
        option, _, value = line.removeprefix("#EXTVLCOPT:").partition("=")
        if line.startswith("#EXTVLCOPT:") and option == "http-referrer":
            headers["Referer"] = value
        elif line.startswith("#EXTVLCOPT:") and option == "http-user-agent":
            headers["User-Agent"] = value
    return headers


def open_stream(url, headers, size):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as response:
        return response.geturl(), response.read(size)


def is_dead_error(error):
    """True only for failures that mean the stream is gone, not just unreachable from here."""
    if isinstance(error, urllib.error.HTTPError):
        return error.code in DEAD_HTTP_CODES
    # the server's name no longer exists, or nothing answers on its port
    return isinstance(getattr(error, "reason", error), (socket.gaierror, ConnectionRefusedError))


def stream_is_dead(lines, stream_url):
    """Fetches the stream like a player. For an HLS playlist the first entry is
    fetched too, since a playlist can load while the video behind it is gone."""
    headers = player_headers(lines)
    try:
        final_url, body = open_stream(stream_url, headers, 4096)
    except Exception as error:
        return is_dead_error(error)
    text = body.decode("utf-8", "ignore")
    if text.lstrip().lower().startswith(("<!doctype html", "<html")):
        return True  # the link leads to a web page, not a stream
    if "#EXTM3U" not in text[:200]:
        return False  # raw video, which starts with binary data
    entry = next((l.strip() for l in text.splitlines() if l.strip() and not l.startswith("#")), None)
    if entry is None:
        return "#EXTINF" not in text and "#EXT-X-MEDIA" not in text  # an empty playlist
    try:
        open_stream(urllib.parse.urljoin(final_url, entry), headers, 512)
    except Exception as error:
        return is_dead_error(error)
    return False


def drop_dead_streams(channels):
    """Returns the channels whose stream still works. Anything that fails is
    tried once more, so a brief hiccup doesn't drop a channel for a day."""
    def dead(channel):
        return stream_is_dead(*channel)

    with concurrent.futures.ThreadPoolExecutor(32) as pool:
        suspects = [c for c, is_dead in zip(channels, pool.map(dead, channels)) if is_dead]
        suspects = [c for c, is_dead in zip(suspects, pool.map(dead, suspects)) if is_dead]

    if len(suspects) > MAX_DEAD_SHARE * len(channels):
        print(f"{len(suspects)} of {len(channels)} streams failed, too many to trust; keeping them all.")
        return channels
    gone = {id(c) for c in suspects}
    print(f"Dropped {len(suspects)} channels whose stream is gone.")
    return [c for c in channels if id(c) not in gone]


def build_playlist():
    allowed = allowed_streams()
    seen_urls = set()
    channels = []
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
            channels.append((lines, stream_url))

    if CHECK_STREAMS:
        channels = drop_dead_streams(channels)

    count = len(channels)
    if count < MIN_CHANNELS:
        sys.exit(f"Only {count} channels found, expected at least {MIN_CHANNELS}. Keeping the existing playlist.")

    output = ["#EXTM3U"]
    for lines, _ in channels:
        output.extend(lines)
    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(output) + "\n")
    print(f"Wrote {count} channels to {OUTPUT_FILE}")


if __name__ == "__main__":
    build_playlist()

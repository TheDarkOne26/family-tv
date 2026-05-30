import os
import re

input_file = os.path.join(".", "scraped_raw.m3u")
output_file = os.path.join(".", "family_safe.m3u")

EPG_URLS = [
    "https://tvpass.org/epg.xml",
    "https://worker-9dd4.onrender.com/guide.xml.gz"
]

# Channels to keep (tvg-id values from your playlist)
ALLOWED_IDS = {
    "ae-us-eastern-feed", "abc-wabc-new-york-ny", "amc-eastern-feed",
    "cartoon-network-usa-eastern-feed", "cbs-wcbs-new-york-ny",
    "cinemax-eastern-feed", "cnn", "comedy-central-us-eastern-feed",
    "discovery-channel-us-eastern-feed", "disney-eastern-feed",
    "espn", "espn2", "fox-news", "fox-sports-1", "fox-sports-2",
    "hbo-eastern-feed", "hgtv-usa-eastern-feed",
    "history-channel-us-eastern-feed", "mtv-usa-eastern-feed",
    "national-geographic-us-eastern", "nbc-wnbc-new-york-ny",
    "nfl-network", "nfl-redzone", "nickelodeon-usa-east-feed",
    "paramount-with-showtime-eastern-feed", "starz-eastern",
    "tnt-eastern-feed", "usa-network-east-feed",
    "disney-junior-usa-east", "cartoon-network-usa-eastern-feed",
    "nick-jr-east", "animal-planet-us-east", "tlc-usa-eastern",
    "hallmark-eastern-feed", "lifetime-network-us-eastern-feed"
}

# Map group-title values to clean categories
GROUP_MAP = {
    "Live": None  # will be replaced based on tvg-id
}

SPORTS_IDS = {"espn", "espn2", "fox-sports-1", "fox-sports-2", "nfl-network", "nfl-redzone"}
KIDS_IDS = {"cartoon-network-usa-eastern-feed", "disney-eastern-feed", "nickelodeon-usa-east-feed", "nick-jr-east", "disney-junior-usa-east"}
MOVIE_IDS = {"hbo-eastern-feed", "cinemax-eastern-feed", "starz-eastern", "amc-eastern-feed", "paramount-with-showtime-eastern-feed"}
NEWS_IDS = {"cnn", "abc-wabc-new-york-ny", "cbs-wcbs-new-york-ny", "nbc-wnbc-new-york-ny", "fox-news"}

def get_group(tvg_id):
    if tvg_id in SPORTS_IDS:
        return "Sports"
    if tvg_id in KIDS_IDS:
        return "Kids"
    if tvg_id in MOVIE_IDS:
        return "Movies"
    if tvg_id in NEWS_IDS:
        return "News"
    return "Entertainment"

def build_clean_playlist(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    output_lines = []
    # Write single clean header with all EPG sources combined
    epg_combined = ",".join(EPG_URLS)
    output_lines.append(f'#EXTM3U x-tvg-url="{epg_combined}"\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Skip any extra EXTM3U headers mid-file
        if line.startswith("#EXTM3U"):
            i += 1
            continue

        if line.startswith("#EXTINF"):
            # Extract tvg-id
            match = re.search(r'tvg-id="([^"]*)"', line)
            if match:
                tvg_id = match.group(1)
                if tvg_id in ALLOWED_IDS:
                    # Fix the group-title
                    correct_group = get_group(tvg_id)
                    line = re.sub(r'group-title="[^"]*"', f'group-title="{correct_group}"', line)
                    output_lines.append(line + "\n")
                    # Write the URL on the next line
                    if i + 1 < len(lines):
                        output_lines.append(lines[i + 1])
                    i += 2
                    continue
        i += 1

    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(output_lines)

    print(f"Done. Wrote {sum(1 for l in output_lines if l.startswith('#EXTINF'))} channels.")

build_clean_playlist(input_file, output_file)

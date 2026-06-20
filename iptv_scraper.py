import os
import re
import urllib.request

input_file = os.path.join(".", "scraped_raw.m3u")
output_file = os.path.join(".", "family_safe.m3u")

# The list of category URLs you want to pull from
SOURCE_URLS = [
    "https://iptv-org.github.io/iptv/categories/sports.m3u",
    "https://iptv-org.github.io/iptv/categories/movies.m3u",
    "https://iptv-org.github.io/iptv/categories/kids.m3u",
    "https://iptv-org.github.io/iptv/categories/entertainment.m3u",
    "https://iptv-org.github.io/iptv/categories/comedy.m3u",
    "https://iptv-org.github.io/iptv/categories/family.m3u",
    "https://iptv-org.github.io/iptv/categories/general.m3u"
]

EPG_URLS = [
    "https://tvpass.org/epg.xml",
    "https://worker-9dd4.onrender.com/guide.xml.gz"
]

# (Temporarily ignored while restrictions are lifted, but kept here for your future reference)
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
    "disney-junior-usa-east", "nick-jr-east", "animal-planet-us-east", 
    "tlc-usa-eastern", "hallmark-eastern-feed", "lifetime-network-us-eastern-feed"
}

SPORTS_IDS = {"espn", "espn2", "fox-sports-1", "fox-sports-2", "nfl-network", "nfl-redzone"}
KIDS_IDS = {"cartoon-network-usa-eastern-feed", "disney-eastern-feed", "nickelodeon-usa-east-feed", "nick-jr-east", "disney-junior-usa-east"}
MOVIE_IDS = {"hbo-eastern-feed", "cinemax-eastern-feed", "starz-eastern", "amc-eastern-feed", "paramount-with-showtime-eastern-feed"}
NEWS_IDS = {"cnn", "abc-wabc-new-york-ny", "cbs-wcbs-new-york-ny", "nbc-wnbc-new-york-ny", "fox-news"}

def get_group(tvg_id):
    # Quick cleanup to handle different variations of IDs lowercase
    tvg_id_lower = tvg_id.lower()
    for sport in SPORTS_IDS:
        if sport in tvg_id_lower: return "Sports"
    for kid in KIDS_IDS:
        if kid in tvg_id_lower: return "Kids"
    for movie in MOVIE_IDS:
        if movie in tvg_id_lower: return "Movies"
    for news in NEWS_IDS:
        if news in tvg_id_lower: return "News"
    return "Entertainment"

def download_and_combine_playlists():
    print("Downloading and combining playlists...")
    combined_content = []
    
    for url in SOURCE_URLS:
        print(f"Fetching {url}...")
        try:
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req) as response:
                content = response.read().decode('utf-8')
                combined_content.append(content)
        except Exception as e:
            print(f"Failed to download {url}: {e}")
            
    if combined_content:
        with open(input_file, 'w', encoding='utf-8') as out_file:
            for text in combined_content:
                out_file.write(text)
                out_file.write("\n")
        print("Successfully downloaded and combined all lists!")
        return True
    return False

def build_clean_playlist(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    output_lines = []
    epg_combined = ",".join(EPG_URLS)
    output_lines.append(f'#EXTM3U x-tvg-url="{epg_combined}"\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("#EXTM3U"):
            i += 1
            continue

        if line.startswith("#EXTINF"):
            # Extract tvg-id just to handle sorting groups automatically
            match = re.search(r'tvg-id="([^"]*)"', line)
            tvg_id = match.group(1) if match else ""
            
            # --- RESTRICTIONS LIFTED ---
            # Group assignment sorting happens here
            correct_group = get_group(tvg_id)
            
            # If the channel already has a group-title parameter, modify it. If not, inject it.
            if 'group-title="' in line:
                line = re.sub(r'group-title="[^"]*"', f'group-title="{correct_group}"', line)
            else:
                line = line.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="{correct_group}"')
                
            output_lines.append(line + "\n")
            
            # Grabs the streaming stream link on the immediate next line
            if i + 1 < len(lines):
                output_lines.append(lines[i + 1].strip() + "\n")
            i += 2
            continue
        i += 1

    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(output_lines)

    print(f"Done. Wrote {sum(1 for l in output_lines if l.startswith('#EXTINF'))} channels to your open list.")

# --- Main Execution ---
if download_and_combine_playlists():
    build_clean_playlist(input_file, output_file)
else:
    print("Script stopped because the raw files could not be retrieved.")

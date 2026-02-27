import requests

# We added a "Header" to trick the servers into thinking we are a Chrome browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Mixing the premium 'TheTVApp' with reliable variety sources
SOURCES = [
    "https://tvpass.org/playlist/m3u",              # TheTVApp (Premium/Sports)
    "https://iptv-org.github.io/iptv/languages/eng.m3u", # English Master
    "https://apsattv.com/ssungusa.m3u",             # Samsung TV Plus
    "https://i.mjh.nz/all/raw.m3u8"                 # Roku/Plex Mix
]

def build_ultimate_list():
    all_content = []
    EPG = "https://iptv-org.github.io/epg/guides/all.xml.gz"

    for url in SOURCES:
        print(f"Fetching: {url}")
        try:
            # We add 'headers=HEADERS' here to prevent getting blocked
            r = requests.get(url, headers=HEADERS, timeout=25)
            if r.status_code == 200:
                lines = r.text.splitlines()
                # Skip the first line (#EXTM3U) and add the rest
                all_content.extend(lines[1:])
                print(f"Successfully added content from {url}")
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            continue

    # Write the final file for your TV
    with open("family_safe.m3u", "w", encoding="utf-8") as f:
        f.write(f'#EXTM3U x-tvg-url="{EPG}"\n')
        for line in all_content:
            f.write(line + "\n")
    
    print(f"MISSION SUCCESS: Created list with {len(all_content)} lines!")

if __name__ == "__main__":
    build_ultimate_list()

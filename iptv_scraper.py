import requests

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# The heavy hitters: Premium, Variety, and the Global English list
SOURCES = [
    "https://tvpass.org/playlist/m3u",              # TheTVApp (Premium)
    "https://iptv-org.github.io/iptv/languages/eng.m3u", # English Only
    "https://apsattv.com/ssungusa.m3u",             # Samsung TV Plus
    "https://i.mjh.nz/all/raw.m3u8"                 # Roku/Plex Mix
]

def build_trimmed_list():
    all_content = []
    EPG = "https://iptv-org.github.io/epg/guides/all.xml.gz"

    for url in SOURCES:
        print(f"Fetching: {url}")
        try:
            r = requests.get(url, headers=HEADERS, timeout=25)
            if r.status_code == 200:
                lines = r.text.splitlines()
                # We skip the first line (#EXTM3U)
                all_content.extend(lines[1:])
        except:
            continue

    # Write the clean file
    with open("family_safe.m3u", "w", encoding="utf-8") as f:
        f.write(f'#EXTM3U x-tvg-url="{EPG}"\n')
        
        # This logic ensures we only write lines that are English or Sports
        for i in range(len(all_content)):
            line = all_content[i]
            if line.startswith("#EXTINF"):
                title = line.upper()
                # We keep the channel if it's English OR if it's a Sports channel
                if "ENG" in title or "USA" in title or "SPORTS" in title or "TVPASS" in title:
                    f.write(line + "\n")
                    f.write(all_content[i+1] + "\n") # Write the URL line below it
    
    print("Optimization Complete: Non-English junk removed!")

if __name__ == "__main__":
    build_trimmed_list()

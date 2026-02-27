import requests
import m3u8

# A mix of the most stable sources for variety
SOURCES = [
    "https://tvpass.org/playlist/m3u",
    "https://apsattv.com/ssungusa.m3u",
    "https://i.mjh.nz/all/raw.m3u8",
    "https://iptv-org.github.io/iptv/index.m3u"
]

def build_ultimate_list():
    working_channels = []
    seen_urls = set()
    EPG_URL = "https://iptv-org.github.io/epg/guides/all.xml.gz"

    for url in SOURCES:
        print(f"Scraping: {url}")
        try:
            # We give it 30 seconds to respond so it doesn't quit early
            r = requests.get(url, timeout=30)
            playlist = m3u8.loads(r.text)
            
            for ch in playlist.segments:
                if ch.uri not in seen_urls:
                    title = ch.title.upper() if ch.title else "UNKNOWN CHANNEL"
                    
                    # Simpler categorization so nothing gets left out
                    if any(word in title for word in ["USA", "NBC", "ABC", "CBS", "FOX", "ESPN"]):
                        cat = "USA"
                    elif "SPORTS" in title:
                        cat = "SPORTS"
                    else:
                        cat = "INTERNATIONAL & VARIETY"
                    
                    # We add EVERY channel we find
                    ch.category = cat
                    working_channels.append(ch)
                    seen_urls.add(ch.uri)
        except Exception as e:
            print(f"Skipping {url} due to error: {e}")
            continue

    with open("family_safe.m3u", "w", encoding="utf-8") as f:
        f.write(f'#EXTM3U x-tvg-url="{EPG_URL}"\n')
        for ch in working_channels:
            f.write(f'#EXTINF:-1 group-title="{ch.category}",{ch.title}\n{ch.uri}\n')
    
    print(f"SUCCESS: Created a list with {len(working_channels)} channels!")

if __name__ == "__main__":
    build_ultimate_list()

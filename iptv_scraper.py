import requests
import m3u8

# Added even more sources for maximum variety
SOURCES = [
    "https://tvpass.org/playlist/m3u",
    "https://apsattv.com/ssungusa.m3u",
    "https://i.mjh.nz/all/raw.m3u8",
    "https://iptv-org.github.io/iptv/index.m3u",
    "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlist.m3u8"
]

def build_ultimate_list():
    working_channels = []
    seen_urls = set()
    EPG_URL = "https://iptv-org.github.io/epg/guides/all.xml.gz"

    for url in SOURCES:
        print(f"Trying source: {url}")
        try:
            # Added a longer timeout (30s) in case a source is slow
            r = requests.get(url, timeout=30)
            playlist = m3u8.loads(r.text)
            
            for ch in playlist.segments:
                if ch.uri not in seen_urls:
                    title = ch.title.upper() if ch.title else "UNKNOWN"
                    
                    # New Logic: If it has a title, we take it!
                    if any(word in title for word in ["USA", "NBC", "ABC", "CBS", "FOX", "ESPN", "SPORTS"]):
                        cat = "USA & SPORTS"
                    elif any(word in title for word in ["KIDS", "NICK", "DISNEY", "CARTOON"]):
                        cat = "KIDS"
                    else:
                        cat = "INTERNATIONAL & VARIETY"
                    
                    ch.category = cat
                    working_channels.append(ch)
                    seen_urls.add(ch.uri)
        except Exception as e:
            print(f"Error on {url}: {e}")
            continue

    # Final write to file
    with open("family_safe.m3u", "w", encoding="utf-8") as f:
        f.write(f'#EXTM3U x-tvg-url="{EPG_URL}"\n')
        for ch in working_channels:
            f.write(f'#EXTINF:-1 group-title="{ch.category}",{ch.title}\n{ch.uri}\n')
    print(f"Done! Created list with {len(working_channels)} channels.")

if __name__ == "__main__":
    build_ultimate_list()

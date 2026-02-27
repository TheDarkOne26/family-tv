import requests
import m3u8

SOURCES = [
    "https://tvpass.org/playlist/m3u",
    "https://apsattv.com/ssungusa.m3u",
    "https://i.mjh.nz/all/raw.m3u8",
    "https://iptv-org.github.io/iptv/index.m3u"
]

def build_categorized_list():
    working_channels = []
    seen_urls = set()
    
    # The EPG link we want the TV app to use
    EPG_URL = "https://iptv-org.github.io/epg/guides/all.xml.gz"

    for url in SOURCES:
        try:
            r = requests.get(url, timeout=15)
            playlist = m3u8.loads(r.text)
            for ch in playlist.segments:
                if ch.uri not in seen_urls:
                    title = ch.title.upper()
                    
                    # Logic to determine the Category (Group)
                    if any(word in title for word in ["USA", "NBC", "ABC", "CBS", "FOX", "ESPN"]):
                        category = "USA"
                    elif "SPORTS" in title:
                        category = "SPORTS"
                    elif any(word in title for word in ["KIDS", "NICK", "DISNEY"]):
                        category = "KIDS"
                    else:
                        category = "INTERNATIONAL"
                    
                    # Store the channel with its assigned category
                    ch.category = category 
                    working_channels.append(ch)
                    seen_urls.add(ch.uri)
        except:
            continue

    # Write the file with the EPG header
    with open("family_safe.m3u", "w", encoding="utf-8") as f:
        f.write(f'#EXTM3U x-tvg-url="{EPG_URL}"\n')
        for ch in working_channels:
            # group-title creates the folders in the TV app
            f.write(f'#EXTINF:-1 group-title="{ch.category}",{ch.title}\n{ch.uri}\n')

build_categorized_list()

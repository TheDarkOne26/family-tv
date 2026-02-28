import requests
import re

# We are using the massive, clean sources
SOURCES = [
    "https://iptv-org.github.io/iptv/languages/eng.m3u",       
    "https://iptv-org.github.io/iptv/categories/sports.m3u",   
    "https://iptv-org.github.io/iptv/categories/kids.m3u"      
]

def build_ultimate_roku_list():
    print("Starting the ultimate scraper...")
    
    with open("family_safe.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        channel_count = 0
        
        for url in SOURCES:
            print(f"Fetching from: {url}")
            try:
                response = requests.get(url, timeout=20)
                if response.status_code == 200:
                    lines = response.text.splitlines()
                    
                    for i in range(len(lines)):
                        if lines[i].startswith("#EXTINF"):
                            if i + 1 < len(lines):
                                stream_url = lines[i+1].strip()
                                
                                # THE BOUNCER: Only allow true video streams
                                if stream_url.startswith("http") and any(ext in stream_url.lower() for ext in [".m3u8", ".ts"]):
                                    
                                    # THE STRIPPER: Remove all the heavy metadata and logos
                                    # We just keep the channel name (everything after the last comma)
                                    channel_name = lines[i].split(",")[-1].strip()
                                    
                                    # Write the clean, lightweight entry
                                    f.write(f'#EXTINF:-1,{channel_name}\n')
                                    f.write(f'{stream_url}\n')
                                    channel_count += 1
            except Exception as e:
                print(f"Failed to fetch {url}: {e}")
                
    print(f"Success! Built a Roku-Safe playlist with {channel_count} channels.")

if __name__ == "__main__":
    build_ultimate_roku_list()

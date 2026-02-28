import requests

# We are bringing back the massive lists. 
# These are open-source and regularly updated with direct .m3u8 streams.
SOURCES = [
    "https://iptv-org.github.io/iptv/languages/eng.m3u",       # Massive English list
    "https://iptv-org.github.io/iptv/categories/sports.m3u",   # Global Sports
    "https://iptv-org.github.io/iptv/categories/kids.m3u"      # Kids & Family
]

def build_massive_playlist():
    print("Starting the massive scraper...")
    
    with open("family_safe.m3u", "w", encoding="utf-8") as f:
        # Write the required header once
        f.write("#EXTM3U\n")
        
        channel_count = 0
        
        for url in SOURCES:
            print(f"Fetching from: {url}")
            try:
                response = requests.get(url, timeout=20)
                if response.status_code == 200:
                    lines = response.text.splitlines()
                    
                    # Loop through the downloaded list
                    for i in range(len(lines)):
                        if lines[i].startswith("#EXTINF"):
                            # Check the very next line for the URL
                            if i + 1 < len(lines):
                                stream_url = lines[i+1].strip()
                                
                                # THE BOUNCER: Only allow true video streams (.m3u8, .ts, etc.)
                                # This is what stops the Roku from crashing!
                                if stream_url.startswith("http") and any(ext in stream_url.lower() for ext in [".m3u8", ".ts", ".mp4", ".mkv"]):
                                    f.write(lines[i] + "\n")
                                    f.write(stream_url + "\n")
                                    channel_count += 1
            except Exception as e:
                print(f"Failed to fetch {url}: {e}")
                
    print(f"Success! Built a massive playlist with {channel_count} clean stream links.")

if __name__ == "__main__":
    build_massive_playlist()

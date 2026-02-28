import requests

# We are pulling the TVPass list PLUS the massive global databases
SOURCES = [
    "https://tvpass.org/playlist/m3u",
    "https://iptv-org.github.io/iptv/languages/eng.m3u",
    "https://iptv-org.github.io/iptv/categories/sports.m3u",
    "https://iptv-org.github.io/iptv/categories/kids.m3u"
]

def build_massive_pc_list():
    print("Starting the unrestricted scraper for PC...")
    # Using a User-Agent to ensure TVPass doesn't block the request
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    with open("family_safe.m3u", "w", encoding="utf-8") as f:
        # Write the master header once
        f.write("#EXTM3U\n")
        
        channel_count = 0
        
        for url in SOURCES:
            print(f"Fetching from: {url}")
            try:
                response = requests.get(url, headers=headers, timeout=20)
                if response.status_code == 200:
                    lines = response.text.splitlines()
                    
                    for line in lines:
                        # Skip the individual #EXTM3U headers from the source files
                        if line.strip().upper() == "#EXTM3U":
                            continue
                            
                        # Write everything else directly to the file, keeping all logos and metadata
                        if line.strip() != "":
                            f.write(line + "\n")
                            if line.startswith("#EXTINF"):
                                channel_count += 1
                                
            except Exception as e:
                print(f"Failed to fetch {url}: {e}")
                
    print(f"Success! Built a massive, unrestricted PC playlist with {channel_count} channels.")

if __name__ == "__main__":
    build_massive_pc_list()

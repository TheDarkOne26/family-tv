import requests

# We stick to the 3 most stable sources to keep the list small
SOURCES = [
    "https://tvpass.org/playlist/m3u",
    "https://iptv-org.github.io/iptv/languages/eng.m3u",
    "https://apsattv.com/ssungusa.m3u"
]

def build_roku_list():
    all_content = []
    # We only take the first 250 channels found to save Roku memory
    MAX_CHANNELS = 250 

    for url in SOURCES:
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                lines = r.text.splitlines()[1:] # Skip header
                all_content.extend(lines)
        except:
            continue

    with open("family_safe.m3u", "w", encoding="utf-8") as f:
        f.write('#EXTM3U\n')
        # This only writes the first 250 entries
        count = 0
        for i in range(0, len(all_content), 2):
            if count < MAX_CHANNELS:
                f.write(all_content[i] + "\n")
                f.write(all_content[i+1] + "\n")
                count += 1
    
    print(f"Roku Optimization Complete: {count} channels saved.")

if __name__ == "__main__":
    build_roku_list()

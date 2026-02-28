import requests

# We'll use the most stable source for the family
SOURCE_URL = "https://tvpass.org/playlist/m3u"

def build_slim_list():
    try:
        print("Fetching channels...")
        response = requests.get(SOURCE_URL, timeout=15)
        if response.status_code != 200:
            print("Failed to get data from source.")
            return

        lines = response.text.splitlines()
        
        with open("family_safe.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            
            # We skip the first line (#EXTM3U) and loop through the rest
            for i in range(1, len(lines)):
                line = lines[i]
                
                # If it's a channel info line, we simplify it for Roku
                if line.startswith("#EXTINF"):
                    # We extract JUST the name (everything after the last comma)
                    channel_name = line.split(",")[-1]
                    f.write(f"#EXTINF:-1,{channel_name}\n")
                    
                    # The very next line in an M3U is always the URL
                    if i + 1 < len(lines):
                        f.write(lines[i+1] + "\n")
        
        print("Success! Created a slim, Roku-safe playlist.")

    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    build_slim_list()

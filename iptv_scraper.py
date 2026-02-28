import requests

# We will just pull from the English list for this test
SOURCES = ["https://iptv-org.github.io/iptv/languages/eng.m3u"]

def build_micro_test():
    print("Starting the micro-test scraper...")
    
    with open("family_safe.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        channel_count = 0
        
        for url in SOURCES:
            try:
                response = requests.get(url, timeout=20)
                if response.status_code == 200:
                    lines = response.text.splitlines()
                    
                    for i in range(len(lines)):
                        if lines[i].startswith("#EXTINF"):
                            if i + 1 < len(lines):
                                stream_url = lines[i+1].strip()
                                
                                # 1. The Bouncer: Video streams only
                                if stream_url.startswith("http") and any(ext in stream_url.lower() for ext in [".m3u8", ".ts"]):
                                    channel_name = lines[i].split(",")[-1].strip()
                                    
                                    # 2. THE CHARACTER GUARD: Only allow standard English letters/numbers
                                    # This stops the Roku from panicking on foreign text
                                    if channel_name.isascii():
                                        f.write(f'#EXTINF:-1,{channel_name}\n')
                                        f.write(f'{stream_url}\n')
                                        channel_count += 1
                                        
                                        # 3. THE HARD STOP: Limit to exactly 50 channels for the test
                                        if channel_count >= 50:
                                            print("Successfully saved 50 clean channels.")
                                            return
            except Exception as e:
                print(f"Failed to fetch {url}: {e}")

if __name__ == "__main__":
    build_micro_test()

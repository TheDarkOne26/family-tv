import os
import urllib.request

output_file = os.path.join(".", "family_safe.m3u")

# The list of category URLs to pull from
SOURCE_URLS = [
    "https://iptv-org.github.io/iptv/categories/sports.m3u",
    "https://iptv-org.github.io/iptv/categories/movies.m3u",
    "https://iptv-org.github.io/iptv/categories/kids.m3u",
    "https://iptv-org.github.io/iptv/categories/entertainment.m3u",
    "https://iptv-org.github.io/iptv/categories/comedy.m3u",
    "https://iptv-org.github.io/iptv/categories/family.m3u",
    "https://iptv-org.github.io/iptv/categories/general.m3u"
]

EPG_URLS = [
    "https://tvpass.org/epg.xml",
    "https://worker-9dd4.onrender.com/guide.xml.gz"
]

def download_and_combine_playlists():
    print("Starting completely unrestricted playlist compilation...")
    combined_lines = []
    
    # Create the single master header at the very top with your EPG URLs
    epg_combined = ",".join(EPG_URLS)
    combined_lines.append(f'#EXTM3U x-tvg-url="{epg_combined}"\n')
    
    for url in SOURCE_URLS:
        print(f"Fetching: {url}")
        try:
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req) as response:
                content = response.read().decode('utf-8')
                
                # Process lines raw, dropping only nested #EXTM3U lines so the file remains valid
                for line in content.splitlines():
                    cleaned_line = line.strip()
                    if cleaned_line.startswith("#EXTM3U"):
                        continue
                    if cleaned_line:
                        combined_lines.append(cleaned_line + "\n")
                        
        except Exception as e:
            print(f"Failed to download {url}: {e}")
            
    if len(combined_lines) > 1:
        with open(output_file, 'w', encoding='utf-8') as out_file:
            out_file.writelines(combined_lines)
        
        # Count the number of channels processed (every line starting with #EXTINF)
        channel_count = sum(1 for l in combined_lines if l.startswith("#EXTINF"))
        print(f"Success! Passed 100% of data through. Wrote {channel_count} channels to {output_file}.")
        return True
    
    print("Error: No playlist data was collected.")
    return False

# Run the master compilation pass
download_and_combine_playlists()

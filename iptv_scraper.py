# This version removes the 'heavy' metadata that crashes the Roku
with open("family_safe.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for channel in my_scraped_list:
        # We ONLY keep the Name and the URL. No logos, no IDs.
        f.write(f'#EXTINF:-1,{channel["name"]}\n')
        f.write(f'{channel["url"]}\n')

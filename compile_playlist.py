import requests

# Expanded list of specific sources for Egypt, Saudi, UAE, Arabic, and Global lists
SOURCES = [
    # --- Middle East & North Africa (Specific Countries) ---
    "https://iptv-org.github.io/iptv/countries/eg.m3u",  # Egypt (~65-72 channels)
    "https://iptv-org.github.io/iptv/countries/sa.m3u",  # Saudi Arabia (~24-43 channels)
    "https://iptv-org.github.io/iptv/countries/ae.m3u",  # UAE (~71-81 channels)
    
    # --- Regional & Language Aggregators ---
    "https://iptv-org.github.io/iptv/regions/arab.m3u",   # Arab World (~315 channels)
    "https://iptv-org.github.io/iptv/languages/ara.m3u",  # Arabic Language (~322-345 channels)
    
    # --- International & Global Categories ---
    "https://iptv-org.github.io/iptv/categories/general.m3u", # General International (~1397 channels)
    "https://iptv-org.github.io/iptv/categories/movies.m3u",  # Movies (24/7)
    "https://iptv-org.github.io/iptv/index.m3u"               # The FULL Global Index (10,000+ channels)
]

def build_playlist():
    seen_urls = set()
    output_lines = ["#EXTM3U"]
    total_channels = 0

    for url in SOURCES:
        try:
            print(f"Fetching: {url}")
            # Increased timeout for the massive global list
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            lines = response.text.splitlines()
            
            current_extinf = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith("#EXTINF"):
                    current_extinf = line
                elif not line.startswith("#"):
                    # This is the stream URL
                    if line not in seen_urls:
                        seen_urls.add(line)
                        if current_extinf:
                            output_lines.append(current_extinf)
                        output_lines.append(line)
                        total_channels += 1
                        current_extinf = None
                        
        except Exception as e:
            print(f"Error fetching {url}: {e}")

    # Save the combined playlist
    with open("custom_playlist.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
        
    print(f"Success! Compiled {total_channels} unique channels into custom_playlist.m3u")

if __name__ == "__main__":
    build_playlist()

import requests

# The specific sources you requested
SOURCES = [
    "https://iptv-org.github.io/iptv/regions/arab.m3u",
    "https://iptv-org.github.io/iptv/countries/my.m3u",
    "https://iptv-org.github.io/iptv/categories/movies.m3u"
]

def build_playlist():
    seen_urls = set()
    output_lines = ["#EXTM3U"]
    total_channels = 0

    for url in SOURCES:
        try:
            print(f"Fetching: {url}")
            response = requests.get(url, timeout=20)
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

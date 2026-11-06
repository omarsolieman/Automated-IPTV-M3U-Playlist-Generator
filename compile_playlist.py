import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

SOURCES = [
    "https://iptv-org.github.io/iptv/categories/documentary.m3u",
    "https://iptv-org.github.io/iptv/categories/cooking.m3u",
    "https://iptv-org.github.io/iptv/categories/news.m3u",
    "https://iptv-org.github.io/iptv/categories/movies.m3u",
    "https://iptv-org.github.io/iptv/categories/entertainment.m3u",
    "https://iptv-org.github.io/iptv/countries/my.m3u",
    "https://iptv-org.github.io/iptv/languages/msa.m3u",
    "https://iptv-org.github.io/iptv/regions/asia.m3u",
    "https://iptv-org.github.io/iptv/countries/id.m3u",
    "https://iptv-org.github.io/iptv/countries/sg.m3u",
    "https://iptv-org.github.io/iptv/countries/eg.m3u",
    "https://iptv-org.github.io/iptv/countries/sa.m3u",
    "https://iptv-org.github.io/iptv/countries/ae.m3u",
    "https://iptv-org.github.io/iptv/regions/arab.m3u",
    "https://iptv-org.github.io/iptv/languages/ara.m3u"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 VLC/3.0.20 LibVLC/3.0.20"
}

def check_stream(stream_info):
    extinf, url = stream_info
    try:
        response = requests.head(url, headers=HEADERS, timeout=4, allow_redirects=True)
        if response.status_code == 405:
            response = requests.get(url, headers=HEADERS, timeout=4, stream=True)
        if response.status_code == 200:
            return (extinf, url)
    except Exception:
        pass
    return None

def build_playlist():
    seen_urls = set()
    stream_queue = []

    print("Fetching playlists...")
    for url in SOURCES:
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            response.raise_for_status()
            lines = response.text.splitlines()
            
            current_extinf = None
            for line in lines:
                line = line.strip()
                if not line: continue
                
                if line.startswith("#EXTINF"):
                    current_extinf = line
                elif not line.startswith("#"):
                    if line not in seen_urls and current_extinf:
                        seen_urls.add(line)
                        stream_queue.append((current_extinf, line))
                        current_extinf = None
        except Exception as e:
            print(f"Error fetching {url}: {e}")

    print(f"Found {len(stream_queue)} unique streams. Testing streams now (this takes time)...")
    
    working_streams = []
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(check_stream, stream) for stream in stream_queue]
        
        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            if result:
                working_streams.append(result)
            if i % 100 == 0:
                print(f"Checked {i}/{len(stream_queue)}... Found {len(working_streams)} working.")

    output_lines = ["#EXTM3U"]
    for extinf, url in working_streams:
        output_lines.append(extinf)
        output_lines.append(url)

    with open("custom_playlist.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
        
    print(f"Success! Compiled {len(working_streams)} VERIFIED WORKING channels.")

if __name__ == "__main__":
    build_playlist()

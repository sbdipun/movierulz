from flask import Flask, Response
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

app = Flask(__name__)

BASE_URL = "https://www.5movierulz.soy/"

def extract_title_from_magnet(magnet_link):
    """Extracts movie title from the magnet link's 'dn' parameter."""
    match = re.search(r"dn=([^&]+)", magnet_link)
    return urllib.parse.unquote(match.group(1).replace(".", " ")) if match else "Unknown Title"

def fetch_movie_links_from_page(movie_url):
    """Fetch movie torrent links from a given movie URL."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(movie_url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.RequestException as e:
        print(f"Error fetching {movie_url}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    movie_links = []

    # Find all <a> elements with the download link class
    download_links = soup.find_all('a', class_='mv_button_css')

    for link in download_links:
        magnet_link = link.get('href')
        if magnet_link:
            size_info = link.find('small').text if link.find('small') else 'Unknown Size'
            movie_title = extract_title_from_magnet(magnet_link)
            movie_links.append({
                "title": movie_title,
                "magnet": magnet_link,
                "size": size_info
            })

    return movie_links

@app.route("/")
def home():
    return "5MovieRulz Scraper API is running!"

@app.route("/rss")
def rss_feed():
    """Generate and return the RSS feed with movie torrent links."""
    movie_url = BASE_URL
    torrents = fetch_movie_links_from_page(movie_url)

    if not torrents:
        return Response(
            "<?xml version='1.0' encoding='UTF-8' ?><rss><channel><title>No Data</title></channel></rss>",
            mimetype="application/xml"
        )

    # Create RSS items from the fetched torrent links
    rss_items = "".join(
        f"""
        <item>
            <title>{torrent['title']} ({torrent['size']})</title>
            <link>{torrent['magnet']}</link>
        </item>
        """ for torrent in torrents
    )

    # Construct the full RSS feed
    rss_content = f"""<?xml version="1.0" encoding="UTF-8" ?>
    <rss version="2.0">
        <channel>
            <title>5MovieRulz - Latest Torrents</title>
            <link>{BASE_URL}</link>
            <description>Latest Movie Torrent Links</description>
            {rss_items}
        </channel>
    </rss>
    """

    return Response(rss_content, mimetype="application/xml")

if __name__ == "__main__":
    app.run(debug=True)

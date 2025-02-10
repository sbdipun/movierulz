from flask import Flask, Response
import requests
from bs4 import BeautifulSoup
import re
import urllib.parse

app = Flask(__name__)

BASE_URL = "https://www.5movierulz.soy/"

def extract_title(magnet_link):
    match = re.search(r"dn=([^&]+)", magnet_link)
    return urllib.parse.unquote(match.group(1).replace(".", " ")) if match else "Unknown Title"

def fetch_movie_links(movie_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(movie_url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    links = []

    for a_tag in soup.find_all("a", class_="mv_button_css"):
        magnet_link = a_tag.get("href")
        if magnet_link and magnet_link.startswith("magnet:"):
            title = extract_title(magnet_link)
            size_match = re.search(r"(\d+(\.\d+)?\s?(GB|MB|TB|KB))", a_tag.text, re.I)
            size = size_match.group(1) if size_match else "Unknown Size"
            links.append({"title": title, "magnet": magnet_link, "size": size})

    return links

@app.route("/")
def home():
    return "5MovieRulz Scraper API is running!"

@app.route("/rss")
def rss_feed():
    movie_url = BASE_URL
    torrents = fetch_movie_links(movie_url)

    if not torrents:
        return Response("<?xml version='1.0' encoding='UTF-8' ?><rss><channel><title>No Data</title></channel></rss>", mimetype="application/xml")

    rss_items = "".join(
        f"""
        <item>
            <title>{torrent['title']} ({torrent['size']})</title>
            <link>{torrent['magnet']}</link>
        </item>
        """ for torrent in torrents
    )

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

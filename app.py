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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(movie_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Debug: Print out the HTML of the movie page
    print(f"Fetching movie links from: {movie_url}")
    print(soup.prettify())  # Inspect the structure of the page

    movie_links = []

    # Find all <a> elements with class "mv_button_css"
    download_links = soup.find_all('a', class_='mv_button_css')

    for link in download_links:
        magnet_link = link.get('href')
        if not magnet_link:
            continue  # Skip if no href attribute

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

from flask import Flask, Response
import requests
from bs4 import BeautifulSoup
import urllib.parse

app = Flask(__name__)

BASE_URL = "https://www.5movierulz.soy/"

def extract_title_from_magnet(magnet_link):
    """Extracts movie title from the magnet link's 'dn' parameter."""
    parsed_url = urllib.parse.urlparse(magnet_link)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    title = query_params.get('dn', ['Unknown Title'])[0]
    return title.replace('.', ' ')  # Replace dots with spaces for readability

def fetch_movie_links(movie_url):
    """Fetches movie torrent magnet links from a specific movie page."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(movie_url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch {movie_url}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    movie_links = []

    # Find all <a> elements with class "mv_button_css"
    download_links = soup.find_all('a', class_='mv_button_css')

    for link in download_links:
        magnet_link = link.get('href')
        if not magnet_link:
            continue

        size_info = link.find('small').text if link.find('small') else 'Unknown Size'
        movie_title = extract_title_from_magnet(magnet_link)

        movie_links.append({
            "title": movie_title,
            "magnet": magnet_link,
            "size": size_info
        })

    return movie_links

@app.route("/rss", methods=["GET"])
def rss_feed():
    """Generate an RSS feed with movie torrent links."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(BASE_URL, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch homepage: {e}")
        return Response("<?xml version='1.0' encoding='UTF-8' ?><rss><channel><title>No Data</title></channel></rss>", mimetype="application/xml")

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all movie links
    movie_elements = soup.find_all('div', class_='boxed film')

    all_movies = []

    for movie in movie_elements:
        title_tag = movie.find('a')
        if title_tag:
            movie_link = title_tag.get('href', '')

            if movie_link:
                movie_links = fetch_movie_links(movie_link)
                all_movies.extend(movie_links)

    if not all_movies:
        return Response(
            "<?xml version='1.0' encoding='UTF-8' ?><rss><channel><title>No Data</title></channel></rss>",
            mimetype="application/xml"
        )

    # Construct RSS items
    rss_items = "".join(
        f"""
        <item>
            <title>{torrent['title']} ({torrent['size']})</title>
            <link>{torrent['magnet']}</link>
        </item>
        """ for torrent in all_movies
    )

    # Complete RSS structure
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

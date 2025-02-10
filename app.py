from flask import Flask, jsonify, render_template
import requests
from bs4 import BeautifulSoup
import urllib.parse

app = Flask(__name__)

def extract_title_from_magnet(magnet_link):
    """Extracts movie title from the magnet link's 'dn' parameter."""
    parsed_url = urllib.parse.urlparse(magnet_link)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    title = query_params.get('dn', ['Unknown Title'])[0]
    return title.replace('.', ' ')  # Replace dots with spaces for readability

def fetch_movie_links(movie_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(movie_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    movie_links = []

    # Find all <a> elements with class "mv_button_css"
    download_links = soup.find_all('a', class_='mv_button_css')

    for link in download_links:
        magnet_link = link.get('href')
        size_info = link.find('small').text if link.find('small') else 'Unknown Size'
        movie_title = extract_title_from_magnet(magnet_link)

        movie_links.append({
            "title": movie_title,
            "magnet": magnet_link,
            "size": size_info
        })

    return movie_links

@app.route('/')
def index():
    url = 'https://www.5movierulz.soy/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
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

    return render_template('index.html', movies=all_movies)

@app.route('/api/movies')
def api_movies():
    url = 'https://www.5movierulz.soy/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
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

    return jsonify(all_movies)

if __name__ == "__main__":
    app.run(debug=True)

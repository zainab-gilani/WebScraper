import requests
from bs4 import BeautifulSoup
from requests import Response

# Scraping logic...

headers: set[str] = {
    "User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
}

# Missing closing parenthesis here:
page: Response = requests.get('https://www.ucas.com/explore/search/providers?query=', headers=headers)

soup = BeautifulSoup(page.text, "html.parser")
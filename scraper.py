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

# get all <h1> elements
# on the page
h1_elements = soup.find_all('h1')

# get the element with id="main-title"
main_title_element = soup.find(id='main-title')

# find the footer element
# based on the text it contains
footer_element = soup.find(text={'Powered by WordPress'})

# find all the centered elements
# on the page
centered_element = soup.find_all(class_='text-center')

# get all "li" elements
# in the ".navbar" element
soup.find(class_='navbar').find_all('li')

# get all "li" elements
# in the ".navbar" element
soup.select('.navbar > li')

# class content
# class+ content_details
# class header_header
# class location-display
import requests
from bs4 import BeautifulSoup
from requests import Response

class Course:
    def __init__(self):
        self.name = ""
        self.duration = ""
        self.start_date = ""
        self.link = ""

        self.requirements: [EntryRequirement] = []
    #endef
#endclass

class EntryRequirement:
    def __init__(self):
        # Subject will be name of required subject OR "UCAS Points"
        # when the required_points are stored
        self.subject = ""

        # When subject is "UCAS Points", this is empty
        # instead we use `required_points`
        self.required_grade = ""

        # This will store UCAS points when available
        self.required_points = 0
    #enddef
#endclass

# Represents and stores university details
class University:
    def __init__(self):
        self.name = ""
        self.location = ""
        self.link = ""

        self.courses: [Course] = []
    #enddef

    def print(self):
        print(f"Name: {self.name}, Location: {self.location}, Link: {self.link}")
    #enddef
#endofr

# All universities
all_universities: [University] = []

# Scraping logic...

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
}

# Missing closing parenthesis here:
page: Response = requests.get('https://www.ucas.com/explore/search/providers?query=', headers=headers)

soup = BeautifulSoup(page.text, "html.parser")

# find all the centered elements
# on the page
content_elements = soup.find_all('div', class_='content__details')

#print(content_elements)

# Grab all university content cards from page
for content_element in content_elements:
    # Create and initialize a university object
    university = University()

    # extract the tag <a> HTML elements related to the quote
    link_elements = content_element.select('.header')

    # Extract name and location
    for link_element in link_elements:
        # Uni Name
        university.name = link_element.text

        # Uni Web Link
        university.link = link_element.get('href')
    #endfor

    # Extract Location Name
    loc_elements = content_element.select('.location-display__location')
    for loc_element in loc_elements:
        university.location = loc_element.text
    #enfor

    # TODO:
    # 1. Find all courses (and its basic information and dates)
    # 2. For each course extract grade requirements and UCAS points
    # 3.

    university.print()

    all_universities.append(university)
#endfor


# TODO:
# Save all university as JSON


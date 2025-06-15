#!/usr/bin/python3

import urllib.parse
import requests
import re

from bs4 import BeautifulSoup
from requests import Response
from datetime import date
from JSONWriter import *
from scrape_search_results import *
from models.University import University
from models.Course import Course
from models.EntryRequirement import EntryRequirement

# CONSIDERATIONS:
# 1. Scraping might result in temporary network failures or blocks
# 2.

# All universities
all_universities: [University] = []

# Scraping logic...

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
}

# TODO: I need to a retry mechanism to retry if network fails to connect every 5 seconds until success
# Missing closing parenthesis here:

# https://www.ucas.com/explore/unis/6cadf6e5/the-university-of-law
# link = https://www.ucas.com/explore/unis + code + university name + /courses?studyLevel=undergraduate&studyYear=2026

# Get links of all the result pages we need to crawl. We need to find total number of pages
# Their page results are like this: https://www.ucas.com/explore/search/providers?query=&page=2

# Store links to crawl as UCAS returns few results per page
all_result_pages_to_crawl: [str] = get_links_to_crawl("https://www.ucas.com/explore/search/providers?query=", headers)

for link_to_crawl in all_result_pages_to_crawl:
    # TODO: I need to a retry mechanism to retry if network fails to connect every 5 seconds until success
    # Missing closing parenthesis here:

    # The following is only to obtain the total number of pages to crawl
    page: Response = requests.get(link_to_crawl, headers=headers)

    soup = BeautifulSoup(page.text, "html.parser")

    # find all the centered elements
    # on the page
    content_elements = soup.find_all("div", class_="content__details")

    print(f"Found {len(content_elements)} universities...")

    # Grab all university content cards from page
    for content_element in content_elements:
        # Create and initialize a university object
        university = University()

        # extract the tag <a> HTML elements related to the quote
        link_elements = content_element.select(".header")

        # Extract name and location
        for link_element in link_elements:
            # Uni Name
            university.name = link_element.text

            # Uni Web Link
            university.link = link_element.get("href")

            # Uni Course Page Link

            # Courses are always available for the next academic year
            # Calculate the next year
            next_year = date.today().year + 1

            # Links seem to be the same for 'see all' where all the courses are listed for the university
            # "https://www.ucas.com/explore/search/courses?query=&refinementList%5Bscheme%5D%5B0%5D=Undergraduate&refinementList%5BacademicYear%5D%5B0%5D=2026&refinementList%5Buniversity%5D%5B0%5D=The%20University%20of%20Law"
            # "https://www.ucas.com/explore/search/courses?query=&refinementList%5Bscheme%5D%5B0%5D=Undergraduate&refinementList%5BacademicYear%5D%5B0%5D=2026&refinementList%5Buniversity%5D%5B0%5D=University%20College%20Birmingham"

            encoded_uni_name = urllib.parse.quote(university.name)

            university.link_all_courses = f"https://www.ucas.com/explore/search/courses?query=&refinementList%5Bscheme%5D%5B0%5D=Undergraduate&refinementList%5BacademicYear%5D%5B0%5D={next_year}&refinementList%5Buniversity%5D%5B0%5D={encoded_uni_name}"
        #endfor

        # Extract Location Name
        loc_elements = content_element.select(".location-display__location")
        for loc_element in loc_elements:
            university.location = loc_element.text
        #endfor

        # TODO:
        # 1. Find all courses (and its basic information and dates)
        # 2. For each course extract grade requirements and UCAS points
        # 3.

        relative_link = ""
        real_link = f"https://www.ucas.com{relative_link}"

        all_universities.append(university)

        university.fetch_courses(headers)

        save_json(all_universities)
        print("saved")
        #
        # # ALLOW ONLY ONE UNI TO BE FOUND AND PARSED
        # break
    #endfor

    # # ALLOW ONLY ONE PAGE TO BE FOUND AND PARSED
    # break
#endfor

# DEBUG

print(f"Total unis found: {len(all_universities)}")

# Print all universities obtained
for i, university in all_universities:
    university.print()
#endfor

# Save all university as JSON
#save_json(all_universities)
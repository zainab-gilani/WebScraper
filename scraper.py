#!/usr/bin/env python3

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
from network_helper import get_with_retry

# Development settings: Limit scraping for testing
# These help me test the scraper without downloading everything - saves time during development

# Maximum number of universities with course requirements to collect
MAX_UNIS_WITH_REQ = 20

# Maximum number of universities without requirements to collect (edge cases)
MAX_UNIS_WITHOUT_REQ = 5

# Counters for tracking what we've found
count_with_req = 0
count_without_req = 0

# CONSIDERATIONS:
# 1. Scraping might result in temporary network failures or blocks
# 2.

# All universities - this list will store every University object I create
all_universities: [University] = []

# Scraping logic...

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
}

# NOTE: I originally planned to add a retry system for network failures, but I ended up
# implementing this in the 'network_helper.py' file with the 'get_with_retry' function.
# This handles cases where the connection might fail temporarily.

# https://www.ucas.com/explore/unis/6cadf6e5/the-university-of-law
# link = https://www.ucas.com/explore/unis + code + university name + /courses?studyLevel=undergraduate&studyYear=2026

# Get links of all the result pages we need to crawl. We need to find total number of pages
# Their page results are like this: https://www.ucas.com/explore/search/providers?query=&page=2

# Store links to crawl as UCAS returns few results per page
all_result_pages_to_crawl: [str] = get_links_to_crawl("https://www.ucas.com/explore/search/providers?query=", headers)

for link_to_crawl in all_result_pages_to_crawl:
    # Now I'll loop through each of the results pages I found earlier.
    # This request gets the HTML for one page of university listings.
    page: Response = get_with_retry(link_to_crawl, headers)

    # Check if the request failed
    if page is None:
        print(f"Failed to fetch {link_to_crawl} after multiple retries, skipping...")
        continue
    # endif

    soup = BeautifulSoup(page.text, "html.parser")

    # find all the centered elements
    # on the page
    content_elements = soup.find_all("div", class_="content__details")

    # print(f"Found {len(content_elements)} universities...")

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

            # # Used for testing the parser on a specific university
            # if university.name != "Newcastle University":
            #     continue
            # #endif

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
            
            # Process this university
            break
        #endfor
        
        # # Skip if not Newcastle University (for testing)
        # if university.name != "Newcastle University":
        #     continue
        # #endif

        # Extract Location Name
        loc_elements = content_element.select(".location-display__location")
        for loc_element in loc_elements:
            university.location = loc_element.text
        # endfor

        save_json(all_universities)
        print("SAVED")

        # TODO:
        # 1. Find all courses (and its basic information and dates)
        # 2. For each course extract grade requirements and UCAS points
        # 3.
        university.fetch_courses(headers)

        # Check if this university has courses with requirements
        uni_has_requirements = False

        if len(university.courses) != 0:
            for course in university.courses:
                # Check if course has real requirements
                for req in course.requirements:
                    if req.has_requirements and (req.min_ucas_points > 0 or req.display_grades):
                        uni_has_requirements = True
                        break
                # endfor
                if uni_has_requirements:
                    break
                # endif
            # endfor
        # endif

        # Track what type of university we found and decide if we keep it
        if uni_has_requirements:
            if count_with_req < MAX_UNIS_WITH_REQ:
                count_with_req += 1
                all_universities.append(university)
                print(f"Found university WITH requirements ({count_with_req}/{MAX_UNIS_WITH_REQ}): {university.name}")
            # endif
        else:
            if count_without_req < MAX_UNIS_WITHOUT_REQ:
                count_without_req += 1
                all_universities.append(university)
                print(f"Found university WITHOUT requirements ({count_without_req}/{MAX_UNIS_WITHOUT_REQ}): {university.name}")
            # endif
        # endif

        # Check if we have enough samples
        if count_with_req >= MAX_UNIS_WITH_REQ and count_without_req >= MAX_UNIS_WITHOUT_REQ:
            print(f"\nCollected enough samples: {count_with_req} with requirements, {count_without_req} without")
            break
        # endif
    # endfor

    # Check if we have enough samples after each page
    if count_with_req >= MAX_UNIS_WITH_REQ and count_without_req >= MAX_UNIS_WITHOUT_REQ:
        print("Stopping - collected enough samples from all pages")
        break
    # endif
#endfor

# Summary of what was collected
print("\n")
print("========================================")
print("SCRAPING SUMMARY")
print("========================================")
print(f"Universities with requirements: {count_with_req}/{MAX_UNIS_WITH_REQ}")
print(f"Universities without requirements: {count_without_req}/{MAX_UNIS_WITHOUT_REQ}")
print(f"Total universities collected: {len(all_universities)}")
print("========================================")

# Print all universities obtained
for university in all_universities:
    university.print()
# endfor

save_json(all_universities)
print("saved")

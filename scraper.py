import requests
from bs4 import BeautifulSoup
from requests import Response

# CONSIDERATIONS:
# 1. Scraping might result in temporary network failures or blocks
# 2.

class Course:
    def __init__(self):
        self.name = ""
        self.duration = ""
        self.start_date = ""
        self.link = ""

        self.requirements: [EntryRequirement] = []
    #endef

    def print(self):
        print(f"Course link: {self.link}")
    #enddef
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

    def find_courses(self, link):
        return
    #enddef
#endofr

# All universities
all_universities: [University] = []

# Store links to crawl as UCAS returns few results per page
all_result_pages_to_crawl: [str] =[]

# Scraping logic...

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
}

# TODO: I need to a retry mechanism to retry if network fails to connect every 5 seconds until success
# Missing closing parenthesis here:

# https://www.ucas.com/explore/unis/6cadf6e5/the-university-of-law


exit()

# The following is only to obtain the total number of pages to crawl
page: Response = requests.get("https://www.ucas.com/explore/search/providers?query=", headers=headers)

soup = BeautifulSoup(page.text, "html.parser")

# TODO: Get links of all the result pages we need to crawl. We need to find total number of pages
# Their page results are like this: https://www.ucas.com/explore/search/providers?query=&page=2

page_results = soup.find_all("ul", class_="pagination__list")

total_pages = 0
for page_result in page_results:
    result_items = page_result.find_all("li", class_="pagination__item")

    for result_item in result_items:
        result_links = result_item.find_all("a")

        for item in result_links:
            if item.has_attr("aria-label"):
                page_label = item.attrs["aria-label"]

                if "last page" in page_label:
                    total_pages = int(item.text)
                #endif
            #endif
        #endfor
    #endfor
#endfor

print(f"Total results for search: {total_pages}")

# Build links pages on total pages found in results that we will need to crawl

for i in range(2, total_pages+1):
    next_page = f"https://www.ucas.com/explore/search/providers?query=&page={i}"

    all_result_pages_to_crawl.append(next_page)
#endfor

# We will re-visit this first page to scrape all universities from this page
all_result_pages_to_crawl.insert(0, "https://www.ucas.com/explore/search/providers?query=")

print(all_result_pages_to_crawl)

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
        course = Course()

        # extract the tag <a> HTML elements related to the quote
        link_elements = content_element.select(".header")

        # Extract name and location
        for link_element in link_elements:
            # Uni Name
            university.name = link_element.text

            # Uni Web Link
            university.link = link_element.get("href")
        # endfor

        # Extract Location Name
        loc_elements = content_element.select(".location-display__location")
        for loc_element in loc_elements:
            university.location = loc_element.text
        # endfor

        # TODO:
        # 1. Find all courses (and its basic information and dates)
        # 2. For each course extract grade requirements and UCAS points
        # 3.

        relative_link = ""
        real_link = f"https://www.ucas.com{relative_link}"



        all_universities.append(university)
    # endfor
# endfor

# DEBUG

print(f"Total unis found: {len(all_universities)}")

# Print all universities obtained
for university in all_universities:
    university.print()
#endfor

# TODO:
# Save all university as JSON
import requests
from bs4 import BeautifulSoup
from requests import Response

# CONSIDERATIONS:
# 1. Scraping might result in temporary network failures or blocks
# 2.

class Course:
    def __init__(self):
        self.name = ""
        self.course_type = ""  # e.g. BSc (Hons)
        self.duration = ""
        self.mode = ""  # e.g. Full-time / Part-time
        self.location = ""
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
#endofor

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
# link = https://www.ucas.com/explore/unis + code + university name + /courses?studyLevel=undergraduate&studyYear=2026

#exit()

#page: Response = requests.get("https://www.ucas.com/explore/search/providers?query=", headers=headers)

# Extract courses
page = requests.get("https://www.ucas.com/explore/unis/6cadf6e5/the-university-of-law/courses?studyLevel=undergraduate&studyYear=2026", headers=headers)

soup = BeautifulSoup(page.text, "html.parser")

see_all_buttons = soup.find_all("a")

target_see_all_link = ""

# Gets course page links
for button in see_all_buttons:
    if button.text.strip() == "See all":
        href = button.get("href", "")
        if "explore/search/courses" in href and "The%20University%20of%20Law" in href:
            target_see_all_link = href
            break
        #endif
    #endif
#endfor

print(target_see_all_link)

search_page = requests.get(target_see_all_link, headers=headers)
search_soup = BeautifulSoup(search_page.text, "html.parser")

search_page_results = search_soup.find_all("ul", class_="pagination__list elevation-low")

total_search_pages = 0

for search_page_result in search_page_results:
    result_items = search_page_result.find_all("li", class_="pagination__item")

    for result_item in result_items:
        result_links = result_item.find_all("a")

        for item in result_links:
            if item.has_attr("aria-label"):
                page_label = item.attrs["aria-label"]

                if "last page" in page_label:
                    total_search_pages = int(item.text)
                #endif
            #endif
        #endif
    #endfor
#endfor

print(f"Total results for search: {total_search_pages}")

# Build links pages on total pages found in results that we will need to crawl

for i in range(2, total_search_pages+1):
    next_page = target_see_all_link + f"&page={i}"
    all_result_pages_to_crawl.append(next_page)
#endfor

# We will re-visit this first page to scrape all universities from this page
all_result_pages_to_crawl.insert(0, "https://www.ucas.com/explore/search/courses?query=&refinementList%5Bscheme%5D%5B0%5D=Undergraduate&refinementList%5BacademicYear%5D%5B0%5D=2026&refinementList%5Buniversity%5D%5B0%5D=The%20University%20of%20Law")

print(all_result_pages_to_crawl)

for link_to_crawl in all_result_pages_to_crawl:
    # The following is only to obtain the total number of pages to crawl
    course_page: Response = requests.get(link_to_crawl, headers=headers)
    course_soup = BeautifulSoup(course_page.text, "html.parser")

    # find all the centered elements
    # on the page
    content_elements = course_soup.find_all("div", class_="content__details")

    print(f"Found {len(content_elements)} courses...")

    # Grab all university content cards from page
    for content_element in content_elements:
        course = Course()

        # name
        name_tag = content_element.select_one("p.header__text")
        if name_tag:
            course.name = name_tag.text.strip()

        # link
        link_tag = content_element.select_one("a.header")
        if link_tag:
            course.link = link_tag.get("href")

        # details
        details_tag = content_element.select_one("p.course-display__details")
        if details_tag:
            details = details_tag.get_text(separator=" ·", strip=True)
        else:
            details = "N/A"

        # ucas points
        points_tag = content_element.select_one("p.course-display__tariff")
        if points_tag:
            points = points_tag.text.strip()
        else:
            points = "N/A"

        print(f"Course name: {course.name}")
        print(f"Course link: {course.link}")
        print(f"Details: {details}")
        print(f"UCAS POINTS: {points}")


# The following is only to obtain the total number of pages to crawl
exit()


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

            # Uni Course Page Link
            course.link = university.link + "/courses?studyLevel=undergraduate&studyYear=2026"
            #course.print()
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
    #endfor
#endfor

# DEBUG

exit()
print(f"Total unis found: {len(all_universities)}")

# Print all universities obtained
for university in all_universities:
    university.print()
#endfor

# TODO:
# Save all university as JSON

with open("universities.json", "w", encoding="utf-8") as f:
    f.write("[\n")

    for uni in all_universities:
        f.write("{\n")
        f.write(f'  "name": "{uni.name.strip()}", \n')
        f.write(f'  "location": "{uni.location.strip()}", \n')
        f.write(f'  "link": "{uni.link.strip()}", \n')
        f.write("   }")

        if i < len(all_universities) - 1:
            f.write(",\n")
        else:
            f.write("\n")
        #endif
        f.write("]\n")
    #endfor
# Represents and stores university details
import requests
from bs4 import BeautifulSoup
from requests import Response

from models.Course import Course
from scrape_search_results import *

class University:
    def __init__(self):
        self.name = ""
        self.location = ""
        self.link = ""
        self.link_all_courses = ""

        self.courses: [Course] = []

    # enddef

    def print(self):
        print(f"Name: {self.name}, Location: {self.location}, Link: {self.link}")

    # enddef

    def fetch_courses(self, headers):
        """
        Obtains all links to all courses
        Visits each course page and scrapes course details
        """
        all_result_pages_to_crawl: [str] = get_links_to_crawl(self.link_all_courses, headers)

        print("All course result links:")
        print(all_result_pages_to_crawl)

        for link_to_crawl in all_result_pages_to_crawl:
            # The following is only to obtain the total number of pages to crawl
            course_page: Response = requests.get(link_to_crawl, headers=headers)
            course_soup = BeautifulSoup(course_page.text, "html.parser")

            # find all the centered elements
            # on the page
            content_elements = course_soup.find_all("div", class_="content__details")

            print(f"Found {len(content_elements)} courses...")

            # Extract all university content cards from page
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
                    details = details_tag.get_text(strip=True)
                    parts = [p.strip() for p in details.split("·")]

                    # Splits details into different parts
                    course.course_type = parts[0]
                    course.duration = parts[1]
                    course.mode = parts[2]
                    course.location = parts[3]
                    course.start_date = parts[4]
                else:
                    course.qualification = course.duration = course.mode = course.location = course.start_date = "N/A"
                #endif

                # # ucas points
                # points_tag = content_element.select_one("p.course-display__tariff")
                # if points_tag:
                #     course.required_points = points_tag.text.strip()
                # else:
                #     course.required_points = "N/A"
                # #endif

                self.courses.append(course)

                # ONLY ONE COURSE FOR NOW DURING TESTING
                break
            #endfor

            # ONLY ONE COURSE PAGE FOR NOW DURING TESTING
            break
        #endfor
    # enddef

    def to_json(self) -> dict:
        """
        :return: Creates and returns a JSON dictionary
        """
        courses_json: [dict] = []
        for course in self.courses:
            courses_json.append(course.to_json())
        #endfor

        json = {
            "name": self.name,
            "location": self.location,
            "link": self.link,
            "link_all_courses": self.link_all_courses,
            "courses": courses_json
        }
        return json
    #enddef
# endofor
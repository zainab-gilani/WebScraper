# Represents and stores university details
import requests
import re

from bs4 import BeautifulSoup
from requests import Response
from .Course import Course
from .EntryRequirement import EntryRequirement
from scrape_search_results import get_links_to_crawl
from network_helper import get_with_retry

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
            course_page: Response = get_with_retry(link_to_crawl, headers)
            
            # Check if the request failed
            if course_page is None:
                print(f"Failed to fetch course page {link_to_crawl}, skipping...")
                continue
            #endif
            
            course_soup = BeautifulSoup(course_page.text, "html.parser")

            # find all the centered elements
            # on the page
            content_elements = course_soup.find_all("div", class_="content__details")

            print(f"Found {len(content_elements)} courses...")

            for content_element in content_elements:
                course = Course()

                # name
                name_tag = content_element.select_one("p.header__text")
                if name_tag:
                    course.name = name_tag.text.strip()
                #endif

                # link
                link_tag = content_element.select_one("a.header")
                if link_tag:
                    course.link = link_tag.get("href")
                #endif

                # details
                details_tag = content_element.select_one("p.course-display__details")
                if details_tag:
                    details = details_tag.get_text(strip=True)
                    # Split details and strip whitespace from each part
                    parts = []
                    for p in details.split("·"):
                        stripped_part = p.strip()
                        parts.append(stripped_part)
                    # endfor

                    # Splits details into different parts
                    if len(parts) > 0:
                        course.course_type = parts[0]
                    else:
                        course.course_type = ""
                    #endif
                    
                    if len(parts) > 1:
                        course.duration = parts[1]
                    else:
                        course.duration = ""
                    # endif
                    
                    if len(parts) > 2:
                        course.mode = parts[2]
                    else:
                        course.mode = ""
                    # endif
                    
                    if len(parts) > 3:
                        course.location = parts[3]
                    else:
                        course.location = ""
                    # endif
                    
                    if len(parts) > 4:
                        course.start_date = parts[4]
                    else:
                        course.start_date = ""
                    # endif
                else:
                    course.qualification = course.duration = course.mode = course.location = course.start_date = "N/A"
                #endif

                # ucas points
                points_tag = content_element.select_one("p.course-display__tariff")
                requirement = EntryRequirement()
                requirement.required_points_min = -1
                requirement.required_points_max = -1

                if points_tag:
                    required_points = points_tag.text.strip()

                    try:
                        # Uses RegEx to scrape just the amount of points, not the entire text
                        match = re.search(r"(\d+)\s*-\s*(\d+)", required_points)
                        if match:
                            requirement.required_points_min = int(match.group(1))
                            requirement.required_points_max = int(match.group(2))
                        else:
                            match = re.search(r"(\d+)", required_points)
                            if match:
                                num = int(match.group(1))
                                requirement.required_points_min = num
                            else:
                                requirement.required_points_min = -1
                                requirement.required_points_max = -1
                            #endif
                        #endif
                    except:
                        requirement.required_points_min = -1
                        requirement.required_points_max = -1
                    #endtry
                else:
                    pass
                #endif

                course.requirements.append(requirement)

                self.courses.append(course)

                course.fetch_requirements(headers)
                course.print()

                # # ONLY ONE COURSE FOR NOW DURING TESTING
                # break
            #endfor

            # # ONLY ONE COURSE PAGE FOR NOW DURING TESTING
            # break
        #endfor
    # enddef

    def to_dict(self):
        """Convert to dictionary"""
        courses_list = []
        for course in self.courses:
            course_dict = course.to_dict()
            courses_list.append(course_dict)
        # endfor
        
        result = {
            "name": self.name,
            "location": self.location,
            "link": self.link,
            "link_all_courses": self.link_all_courses,
            "courses": courses_list
        }
        return result
    #enddef
# endclass
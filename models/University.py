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
        """
        Initializes a new University object with empty attributes.

        :return: None
        """
        self.name = ""
        self.location = ""
        self.link = ""
        self.link_all_courses = ""

        self.courses: [Course] = []

    # enddef

    def print(self):
        """
        Prints the university name, location, and link to the console.

        :return: None
        """
        print(f"Name: {self.name}, Location: {self.location}, Link: {self.link}")

    # enddef

    def fetch_courses(self, headers):
        """
        Obtains all links to all courses, visits each course page,
        and scrapes course details including name, type, duration, and requirements.

        :param headers: Request headers dictionary for HTTP requests
        :return: None
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

            # print(f"Found {len(content_elements)} courses...")

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

                # Check if this course has multiple options
                # If details contain "Options" it means there are multiple course variants
                details_tag = content_element.select_one("p.course-display__details")
                if details_tag:
                    details = details_tag.get_text(strip=True)
                    
                    # Check if this is a summary (contains "Options")
                    if "Options" in details or "Option" in details:
                        # This course has multiple options - details will be fetched from the course page
                        # Set temporary placeholder values
                        course.course_type = ""
                        course.duration = ""
                        course.mode = ""
                        course.location = ""
                        course.start_date = ""
                    else:
                        # This is a single course option, parse the details normally
                        # Split details and strip whitespace from each part
                        parts = []
                        for p in details.split("·"):
                            stripped_part = p.strip()
                            parts.append(stripped_part)
                        #endfor

                        # Parse the parts - the order can vary, so we need to be smart about it
                        # Typical patterns:
                        # - BA (Hons) · 3 years · Full-time · Location · September 2026
                        # - BA (Hons) · 2 Years · Full-time (intensive) · 2026
                        
                        # Initialize all fields
                        course.course_type = ""
                        course.duration = ""
                        course.mode = ""
                        course.location = ""
                        course.start_date = ""
                        
                        for part in parts:
                            # Check if it's a qualification (contains BA, BSc, MSc, etc.)
                            is_qualification = False
                            qualification_types = ["BA", "BSc", "MSc", "MA", "BEng", "MEng", "PgDip", "PhD", "MPhil", "LLB", "MBA"]
                            for qual in qualification_types:
                                if qual in part:
                                    is_qualification = True
                                    break
                                #endif
                            #endfor
                            
                            if is_qualification:
                                course.course_type = part
                            else:
                                # Check if it's duration (contains year/years/months)
                                is_duration = False
                                duration_words = ["year", "month"]
                                for dur in duration_words:
                                    if dur in part.lower():
                                        is_duration = True
                                        break
                                    #endif
                                #endfor
                                
                                if is_duration:
                                    course.duration = part
                                else:
                                    # Check if it's mode (contains time/distance/online)
                                    is_mode = False
                                    mode_words = ["full-time", "part-time", "distance", "online", "intensive", "flexible"]
                                    for mode in mode_words:
                                        if mode in part.lower():
                                            is_mode = True
                                            break
                                        #endif
                                    #endfor
                                    
                                    if is_mode:
                                        course.mode = part
                                    else:
                                        # Check if it's just a year (4 digits)
                                        if part.isdigit() and len(part) == 4:
                                            course.start_date = part
                                        else:
                                            # Check if it's a month+year start date
                                            is_start_date = False
                                            month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
                                            for month in month_names:
                                                if month in part:
                                                    is_start_date = True
                                                    break
                                                #endif
                                            #endfor
                                            
                                            if is_start_date:
                                                course.start_date = part
                                            else:
                                                # Otherwise it might be location
                                                # If we haven't set location yet and this doesn't look like other fields
                                                if not course.location and part:
                                                    course.location = part
                                                #endif
                                            #endif
                                        #endif
                                    #endif
                                #endif
                            #endif
                        #endfor
                    #endif
                else:
                    course.course_type = ""
                    course.duration = ""
                    course.mode = ""
                    course.location = ""
                    course.start_date = ""
                #endif

                # Try to get UCAS points from search results page
                points_tag = content_element.select_one("p.course-display__tariff")
                
                # Only create a requirement if we find actual data
                if points_tag:
                    required_points = points_tag.text.strip()
                    
                    # Check if this contains actual points data (not just "N/A" etc)
                    if "N/A" not in required_points and required_points:
                        requirement = EntryRequirement()
                        requirement.min_ucas_points = 0

                        try:
                            # Uses RegEx to scrape just the amount of points, not the entire text
                            match = re.search(r"(\d+)\s*-\s*(\d+)", required_points)
                            if match:
                                requirement.min_ucas_points = int(match.group(1))
                                requirement.has_requirements = True
                            else:
                                match = re.search(r"(\d+)", required_points)
                                if match:
                                    num = int(match.group(1))
                                    requirement.min_ucas_points = num
                                    requirement.has_requirements = True
                                #endif
                            #endif
                            
                            # Only add if we found actual points
                            if requirement.has_requirements:
                                course.requirements.append(requirement)
                            #endif
                        except ValueError:
                            # Don't add anything if number conversion fails
                            pass
                        except Exception as error:
                            # Don't add anything if other parsing fails
                            pass
                        #endtry
                    #endif
                #endif

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
        """
        Converts the University object to a dictionary representation.

        :return: Dictionary containing all university information
        """
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

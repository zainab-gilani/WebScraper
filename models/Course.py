import requests

from bs4 import BeautifulSoup
from requests import Response
from models.EntryRequirement import EntryRequirement


class Course:
    """
    Represents a single course for a university
    and holds course details, such as the name, duration, requirements, etc.
    """
    def __init__(self):
        self.name = ""
        self.course_type = ""  # e.g. BSc (Hons)
        self.duration = ""
        self.mode = ""  # e.g. Full-time / Part-time
        self.location = ""
        self.start_date = ""
        self.link = ""

        self.requirements: [EntryRequirement] = []

    # enddef

    def print(self):
        print(f"Course link: {self.link}")
    # enddef

    def fetch_requirements(self, headers):
        single_course_page: Response = requests.get(self.link, headers=headers)
        single_course_soup = BeautifulSoup(single_course_page.text, "html.parser")

        content_elements = single_course_soup.find_all("ul", class_="accordion--clear")

        # Extract all university content cards from page
        for content_element in content_elements:
            requirement = EntryRequirement()

            # ucas points
            points_tag = content_element.select_one("p.course-display__tariff")
            if points_tag:
                requirement.required_points = points_tag.text.strip()
            else:
                requirement.required_points = "N/A"
            # endif

            grades_tag = content_element.select_one("h2.accordion__label")
            if grades_tag:
                requirement.required_grade = grades_tag.text.strip()
            else:
                requirement.required_grade = "N/A"
            # endif

            self.requirements.append(requirement)

            break
        # endfor
    # enddef

    def to_json(self) -> dict:
        """
        :return: Creates and returns a JSON dictionary
        """

        requirements_json: [dict] = []

        for requirement in self.requirements:
            requirements_json.append(requirement.to_json())
        #endfor

        json = {
            "name": self.name,
            "course_type": self.course_type,
            "duration": self.duration,
            "mode": self.mode,
            "location": self.location,
            "start_date": self.start_date,
            "link": self.link,
            "requirements": requirements_json
        }

        return json
    # enddef
# endclass


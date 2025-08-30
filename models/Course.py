import requests
import re

from bs4 import BeautifulSoup
from requests import Response
from .EntryRequirement import EntryRequirement
from network_helper import get_with_retry


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
        print(f"Entry requirements: {self.requirements}")

    # enddef

    def fetch_requirements(self, headers):
        """
        Fetches requirements for the course from its page
        :param headers: browser headers
        """

        single_course_page: Response = get_with_retry(self.link, headers)

        # Check if the request failed
        if single_course_page is None:
            print(f"Failed to fetch course page {self.link}")
            # Don't add any requirements if we can't fetch the page
            return
        # endif

        single_course_soup = BeautifulSoup(single_course_page.text, "html.parser")

        # Try multiple selectors for entry requirements
        requirement_texts = []

        # Look for accordion labels (common on UCAS)
        accordion_labels = single_course_soup.find_all("h2", class_="accordion__label")
        for label in accordion_labels:
            # Check if any of the qualifications are in the label text
            found_qual = False
            for qual in ["A level", "UCAS", "BTEC"]:
                if qual in label.text:
                    found_qual = True
                    break
                # endif
            # endfor
            if found_qual:
                requirement_texts.append(label.text.strip())
            # endif

        # Look for requirement sections
        req_sections = single_course_soup.find_all(class_=re.compile(r"requirement|entry|qualification", re.I))
        for section in req_sections:
            text = section.get_text(strip=True)
            if text and len(text) < 500:  # Skip really long text
                requirement_texts.append(text)
            # endif

        # Parse all requirement texts and combine into one requirement
        if requirement_texts:
            # Combine all requirement texts into one string
            combined_text = " | ".join(requirement_texts)

            try:
                parsed_req = EntryRequirement.parse(combined_text)
                # Only add if there are actual requirements
                if parsed_req.has_requirements:
                    self.requirements.append(parsed_req)
                # endif
            except Exception as e:
                print(f"Error parsing requirements: {e}")
                # Don't add any requirements if parsing fails
            # endtry
        # endif

    # endfor

    # # Extract all university content cards from page
    # for content_element in content_elements:
    #     requirement = EntryRequirement()
    #
    #     # ucas points
    #     points_tag = content_element.select_one("p.course-display__tariff")
    #     if points_tag:
    #         requirement.required_points = points_tag.text.strip()
    #     else:
    #         requirement.required_points = "N/A"
    #     # endif
    # enddef

    def to_dict(self):
        """Convert to dictionary"""
        requirements_list = []
        for requirement in self.requirements:
            requirement_dict = requirement.to_dict()
            requirements_list.append(requirement_dict)
        # endfor

        result = {
            "name": self.name,
            "course_type": self.course_type,
            "duration": self.duration,
            "mode": self.mode,
            "location": self.location,
            "start_date": self.start_date,
            "link": self.link,
            "requirements": requirements_list
        }
        return result
    # enddef
# endclass
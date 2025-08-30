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

        
        # Look for course options information in different places
        # Check for the options bar with course details
        options_bar = single_course_soup.find("div", class_="options-bar")
        if not options_bar:
            options_bar = single_course_soup.find("div", class_="options-bar-custom")
        
        if options_bar:
            # Extract course details from data-options-bar-item-value attributes
            # Find all elements that have the data-options-bar-item-value attribute
            all_elements = options_bar.find_all()
            elements_with_values = []
            for element in all_elements:
                if element.has_attr("data-options-bar-item-value"):
                    elements_with_values.append(element)
                #endif
            #endfor
            
            if elements_with_values:
                for elem in elements_with_values:
                    value = elem.get("data-options-bar-item-value", "")
                    label_text = elem.get_text(strip=True).lower()
                    
                    # Map the values to course fields based on label
                    if "qualification" in label_text:
                        self.course_type = value
                    elif "location" in label_text:
                        self.location = value
                    elif "start" in label_text:
                        self.start_date = value
                    elif "study mode" in label_text or "mode" in label_text:
                        self.mode = value
                    elif "duration" in label_text:
                        self.duration = value
                    #endif
                #endfor
            #endif
        
        # Check if there's a course options table (for courses with multiple options)
        course_options_table = single_course_soup.find("table")
        if course_options_table:
            # Extract course details from the first row in the table
            tbody = course_options_table.find("tbody")
            if tbody:
                first_row = tbody.find("tr")
                if first_row:
                    tds = first_row.find_all("td")
                    
                    # Different table structures based on number of columns
                    if len(tds) >= 5:  # Standard table with at least 5 columns
                        # Extract details from table columns
                        # Column 0: Location
                        self.location = tds[0].get_text(strip=True)
                        
                        # Column 1: Qualification
                        qual_div = tds[1].find("strong")
                        if qual_div:
                            self.course_type = qual_div.get_text(strip=True)
                        else:
                            # Try getting text directly if no strong tag
                            self.course_type = tds[1].get_text(strip=True)
                        #endif
                        
                        # Column 2: Study mode
                        self.mode = tds[2].get_text(strip=True)
                        
                        # Column 3: Duration
                        self.duration = tds[3].get_text(strip=True)
                        
                        # Column 4: Start date
                        self.start_date = tds[4].get_text(strip=True)
                    #endif
                #endif
            #endif
        #endif

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
                #endif
            #endfor
            if found_qual:
                requirement_texts.append(label.text.strip())
            #endif
        #endfor

        # Look for requirement sections
        # Find sections with class names containing requirement words
        all_divs = single_course_soup.find_all("div")
        req_sections = []
        for div in all_divs:
            if div.has_attr("class"):
                class_names = div.get("class", [])
                for class_name in class_names:
                    class_name_lower = class_name.lower()
                    if ("requirement" in class_name_lower or 
                        "entry" in class_name_lower or 
                        "qualification" in class_name_lower):
                        req_sections.append(div)
                        break
                    #endif
                #endfor
            #endif
        #endfor
        
        for section in req_sections:
            text = section.get_text(strip=True)
            if text and len(text) < 500:  # Skip really long text
                requirement_texts.append(text)
            #endif
        #endfor

        # Parse all requirement texts and combine into one requirement
        if requirement_texts:
            # Combine all requirement texts into one string
            combined_text = " | ".join(requirement_texts)

            try:
                parsed_req = EntryRequirement.parse(combined_text)
                # Only add if there are actual requirements
                if parsed_req.has_requirements:
                    self.requirements.append(parsed_req)
                #endif
            except Exception as e:
                print(f"Error parsing requirements: {e}")
                # Don't add any requirements if parsing fails
            #endtry
        #endif

        # Clean up requirements - remove any empty ones if we have real ones
        self.clean_up_requirements()

    #enddef
    
    def clean_up_requirements(self):
        """Remove empty requirements if we have real ones"""
        if not self.requirements:
            return
        #endif
        
        # Check if we have any real requirements
        has_real_requirements = False
        for req in self.requirements:
            if req.has_requirements:
                has_real_requirements = True
                break
            #endif
        #endfor
        
        # If we have real requirements, remove empty ones
        if has_real_requirements:
            cleaned_requirements = []
            for req in self.requirements:
                if req.has_requirements:
                    cleaned_requirements.append(req)
                #endif
            #endfor
            self.requirements = cleaned_requirements
        #endif
    #enddef

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
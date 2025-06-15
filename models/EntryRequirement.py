import requests
from bs4 import BeautifulSoup
from requests import Response

class EntryRequirement:
    """
    Represents a requirement such as the required grade or UCAS points
    """
    def __init__(self):
        # Subject will be name of required subject OR "UCAS Points"
        # when the required_points are stored
        self.subject = ""

        # When subject is "UCAS Points", this is empty
        # instead we use `required_points`
        # Empty grade means this subject just needs to be taken
        self.required_grade = ""

        # This will store UCAS points when available
        # -1 Means there are NO UCAS point requirements
        # Some courses have a range
        self.required_points_min = -1

        # -1 Means there are NO UCAS point requirements
        # Maximum points (if applicable)
        self.required_points_max = -1
    # enddef

    def fetch_requirements(self):
        pass
    #enddef

    def to_json(self):
        """
        :return: Creates and returns a JSON dictionary
        """
        json = {
            "subject": self.subject,
            "required grade": self.required_grade,
            "minimum required points": self.required_points_min,
            "maximum required points": self.required_points_max
        }
        return json
    # enddef
# endclass
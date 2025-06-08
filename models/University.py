# Represents and stores university details
from models import Course

class University:
    def __init__(self):
        self.name = ""
        self.location = ""
        self.link = ""

        self.courses: [Course] = []

    # enddef

    def print(self):
        print(f"Name: {self.name}, Location: {self.location}, Link: {self.link}")

    # enddef

    def fetch_courses(self):
        pass
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
            "courses": courses_json
        }
        return json
    #enddef
# endofor
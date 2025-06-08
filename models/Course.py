from models import EntryRequirement

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

    def fetch_requirements(self):
        pass
    # enddef

    def to_json(self):
        """
        :return: Creates and returns a JSON dictionary
        """
        json = {
            "name": self.name,
            "course_type": self.course_type,
            "duration": self.duration,
            "mode": self.mode,
            "location": self.location,
            "start_date": self.start_date,
            "link": self.link,
            "requirements": [r.to_json for r in self.requirements]
        }

        return json
    # enddef
# endclass


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
        self.required_grade = ""

        # This will store UCAS points when available
        self.required_points = 0

    # enddef

    def to_json(self):
        """
        :return: Creates and returns a JSON dictionary
        """
        json = {
            "subject": self.subject,
            "required grade": self.required_grade,
            "required points": self.required_points
        }
        return json
    # enddef


# endclass

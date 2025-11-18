"""
This module handles entry requirements for university courses.
It can parse text from UCAS and calculate UCAS points from A-level and BTEC grades.
"""

import re

# UCAS Tariff Points for A-level grades
# Each A-level grade has a certain number of points
A_LEVEL_POINTS = {
    'A*': 56,  # Top grade
    'A': 48,
    'B': 40,
    'C': 32,
    'D': 24,
    'E': 16  # Lowest passing grade
}

# BTEC grade values for calculating UCAS points
# BTEC qualifications have different grades from A-levels
BTEC_GRADE_VALUES = {
    'D*': 56,  # Distinction* (highest)
    'D': 48,  # Distinction
    'M': 32,  # Merit
    'P': 16  # Pass (lowest)
}


class SubjectRequirement:
    """
    Stores information about a specific subject requirement for a course.
    For example, "Mathematics at grade A" or "Chemistry at grade B".
    """

    def __init__(self, subject: str, grade: str):
        """
        Create a new subject requirement.

        :param subject: The name of the subject (e.g., "Mathematics", "Physics")
        :param grade: The grade needed for this subject (e.g., "A", "B", "A*")
        """
        self.subject: str = subject
        self.grade: str = grade

    # enddef

    def to_dict(self) -> dict:
        """
        Convert this subject requirement into a dictionary.
        This makes it easy to save to a database or convert to JSON.

        :return: A dictionary with 'subject' and 'grade' keys
        """
        return {"subject": self.subject, "grade": self.grade}
    # enddef


# endclass

class EntryRequirement:
    """
    Stores all the entry requirements for a university course.
    This includes A-level grades, UCAS points, BTEC grades, and specific subject requirements.
    """

    def __init__(self):
        """
        Create a new entry requirement object with default values.
        """
        # The minimum UCAS points needed to apply (used for filtering in database)
        self.min_ucas_points: int = 0

        # The lowest grade needed across all subjects (e.g., "B" for BBB means B is the minimum)
        self.min_grade_required: str = ""

        # List of specific subjects that must be taken (e.g., Maths at grade A)
        self.subject_requirements: list[SubjectRequirement] = []

        # BTEC grades if the course accepts BTEC (e.g., "DMM", "DDM")
        self.btec_grades: str = ""

        # The grades to show to users on the website (e.g., "AAB", "BBB-BCC")
        self.display_grades: str = ""

        # Whether the course accepts UCAS points (some courses don't)
        self.accepts_ucas: bool = True

        # Whether the course has any entry requirements at all
        self.has_requirements: bool = False

    # enddef

    def add_subject_requirement(self, subject: str, grade: str) -> None:
        """
        Add a requirement for a specific subject to this course.
        If the subject already exists, it updates the grade instead of adding a duplicate.

        :param subject: The name of the subject (e.g., "Mathematics")
        :param grade: The grade required (e.g., "A", "B")
        """
        # Check if we already have a requirement for this subject
        for req in self.subject_requirements:
            if req.subject.lower() == subject.lower():
                # Update the grade for the existing subject
                req.grade = grade
                return

        # Subject doesn't exist yet, so add it as a new requirement
        self.subject_requirements.append(SubjectRequirement(subject, grade))

    # enddef

    def to_dict(self):
        """
        Convert this entry requirement into a dictionary.
        This is useful for saving to a database or exporting as JSON.

        :return: A dictionary containing all the requirement information
        """
        # Convert each subject requirement to a dictionary
        subject_reqs = []
        for req in self.subject_requirements:
            req_dict = req.to_dict()
            subject_reqs.append(req_dict)
        # endfor

        # Build the complete dictionary with all requirement data
        result = {
            "min_ucas_points": self.min_ucas_points,
            "min_grade_required": self.min_grade_required,
            "subject_requirements": subject_reqs,
            "display_grades": self.display_grades,
            "btec_grades": self.btec_grades,
            "accepts_ucas": self.accepts_ucas,
            "has_requirements": self.has_requirements
        }
        return result

    # enddef

    def calculate_a_level_points(self, grades: str) -> int:
        """
        Calculate UCAS points from A-level grades.

        :param grades: A string of A-level grades (e.g., "AAB", "A*AA", "BCC")
        :return: The total UCAS points for these grades
        """
        if not grades:
            return 0
        # endif

        total_points = 0
        grades = grades.strip().upper()

        # Handle A* grades
        while 'A*' in grades:
            total_points += A_LEVEL_POINTS['A*']
            grades = grades.replace('A*', '', 1)
        # endwhile

        # Process remaining grades
        for grade in grades:
            if grade in A_LEVEL_POINTS:
                total_points += A_LEVEL_POINTS[grade]
            # endif
        # endfor

        return total_points

    # enddef

    def find_lowest_grade(self, grades: str) -> str:
        """
        Find the lowest grade in a set of A-level grades.
        For example, in "AAB", the lowest grade is "B".

        :param grades: A string of A-level grades (e.g., "AAB", "BCC")
        :return: The lowest grade found (e.g., "B", "C")
        """
        if not grades:
            return ""
        # endif

        grades = grades.strip().upper()
        grade_order = ['A*', 'A', 'B', 'C', 'D', 'E']
        lowest_grade = ""
        lowest_index = -1

        # Handle A* grades
        while 'A*' in grades:
            if lowest_index < grade_order.index('A*'):
                lowest_grade = 'A*'
                lowest_index = grade_order.index('A*')
            # endif
            grades = grades.replace('A*', '', 1)
        # endwhile

        # Check remaining grades
        for grade in grades:
            if grade in grade_order:
                grade_index = grade_order.index(grade)
                if grade_index > lowest_index:
                    lowest_grade = grade
                    lowest_index = grade_index
                # endif
            # endif
        # endfor

        return lowest_grade

    # enddef

    @staticmethod
    def calculate_btec_points(grades: str) -> int:
        """
        Calculate BTEC points from grade string.
        For example: "DDD" = 144 points, "DMM" = 112 points, "D*D*D*" = 168 points.

        :param grades: A string of BTEC grades (e.g., "DDD", "DMM", "D*D*D*")
        :return: The total UCAS points for these BTEC grades
        """
        if not grades:
            return 0
        # endif

        total = 0

        # Normalize by capitalizing it always
        grades = grades.upper()

        # Handle D* grades first as it's different
        # from the single letter grades
        while 'D*' in grades:
            total += BTEC_GRADE_VALUES['D*']

            # remove it once handled
            grades = grades.replace('D*', '', 1)
        # endwhile

        # Process remaining single grades
        for grade in grades:
            if grade in BTEC_GRADE_VALUES:
                total += BTEC_GRADE_VALUES[grade]
            # endif
        # endfor

        return total

    # enddef

    @staticmethod
    def clean_requirement_text(text: str) -> str:
        """
        Clean up and fix common issues in requirement text from UCAS.
        Sometimes the text is cut off or has formatting problems.

        :param text: The raw requirement text from the website
        :return: Cleaned and properly formatted text
        """
        if not text:
            return ""
        # endif

        # Remove extra whitespace
        text = " ".join(text.split())

        # Handle common truncation issues
        text_lower = text.lower()

        # If we just have "not" by itself, it probably means "not accepted"
        if text_lower.strip() == "not":
            return "Not accepted"
        # endif

        # If we have partial phrases, complete them
        if text_lower.strip() in ["n/a", "na", "not available"]:
            return "Requirements not specified"
        # endif

        # Handle UCAS-specific cases
        if "ucas" in text_lower and "not" in text_lower:
            if "not accepted" not in text_lower:
                return text + " - Not accepted"
            # endif
        # endif

        return text

    # enddef

    @staticmethod
    def parse(requirement_text: str) -> 'EntryRequirement':
        """
        Take requirement text from UCAS and convert it into an EntryRequirement object.
        This is the main function that reads text like "A level - AAB" and figures out
        what grades are needed, what subjects are required, and how many UCAS points it's worth.

        Examples of text it can handle:
        - "A level - AAB" → Needs AAB grades (136 UCAS points)
        - "A level - BCC - BBB" → Needs between BCC and BBB (112-120 points)
        - "UCAS Tariff - 120 points" → Needs 120 UCAS points
        - "A level - AAB including Mathematics at grade A" → Needs AAB with Maths at A

        :param requirement_text: The raw text from the UCAS website
        :return: An EntryRequirement object with all the parsed information
        """
        req = EntryRequirement()

        if not requirement_text:
            req.has_requirements = False
            return req
        # endif

        # Clean the text first
        text = EntryRequirement.clean_requirement_text(requirement_text)

        # Check for no requirements or not accepted
        text_lower = text.lower()
        no_req_phrases = [
            "no formal", "no specific", "no requirement", "requirements not specified",
            "not accepted", "ucas not accepted", "not available",
            # Handle partial text issues
            "not", "n/a"
        ]

        for phrase in no_req_phrases:
            if phrase in text_lower:
                req.has_requirements = False
                # Set a cleaner display message
                if phrase in ["not", "not accepted", "ucas not accepted"]:
                    req.display_grades = "Not accepted"
                else:
                    req.display_grades = "Requirements not specified"
                return req
            # endif
        # endfor

        # Parse A-level requirements
        # This regular expression is designed to find A-level grades in the text.
        # - r'A\s*level\s*[-–]\s*' : It looks for "A level" (with any whitespace), followed by a hyphen.
        # - ([A-Z*]{3,}) : It then looks for a group of at least 3 capital letters or asterisks (e.g., 'AAB', 'BCC'). This is the main grade.
        # - (?:...)? : The last part is an optional group to catch ranges like 'BCC-BBB'.
        a_level_pattern = r'A\s*level\s*[-–]\s*([A-Z*]{3,}(?:\s*[-–]\s*[A-Z*]{3,})?)'
        a_level_match = re.search(a_level_pattern, text, re.IGNORECASE)
        if a_level_match:
            grades = a_level_match.group(1).strip()
            req.display_grades = grades
            req.has_requirements = True

            if "-" in grades:
                # Range like "BCC-BBB" - use minimum
                parts = grades.split("-")
                if len(parts) == 2:
                    min_grades = parts[0].strip()
                    req.min_ucas_points = req.calculate_a_level_points(min_grades)
                    req.min_grade_required = req.find_lowest_grade(min_grades)
                # endif
            else:
                # Single grade like "AAB"
                req.min_ucas_points = req.calculate_a_level_points(grades)
                req.min_grade_required = req.find_lowest_grade(grades)

            # Debug: Uncomment line below to see what text is being analyzed
            # print(f"Analyzing requirement text: {text[:200]}...")

            # Check for subject requirements - multiple patterns needed

            # Pattern 1: "including Chemistry and Mathematics" (Newcastle style)  
            # Look for text containing "including" followed by subject names
            if "including" in text.lower():
                # Find the part after "including"
                including_pos = text.lower().find("including")
                after_including = text[including_pos + 9:].strip()  # 9 = len("including")

                # print(f"Found 'including' text: {after_including[:100]}")

                # Look for subject names before any punctuation or "at grade"
                # Split at common terminators
                terminators = [" at grade", ".", ",", ")", "(", " Further Mathematics is"]
                subjects_text = after_including
                for term in terminators:
                    if term in subjects_text:
                        subjects_text = subjects_text.split(term)[0]
                        break
                    # endif
                # endfor

                # print(f"Extracted subjects text: {subjects_text}")

                # Split subjects on "and" and "or" 
                subject_parts = []

                # Replace "and" and "or" with a separator
                subjects_text = subjects_text.replace(" and ", "|")
                subjects_text = subjects_text.replace(" or ", "|")

                # Split on the separator
                for part in subjects_text.split("|"):
                    clean_part = part.strip()
                    if clean_part and len(clean_part) < 50:
                        subject_parts.append(clean_part)
                    # endif
                # endfor

                # Add each subject with the minimum required grade
                for subject in subject_parts:
                    req.add_subject_requirement(subject, req.min_grade_required)
                    # print(f"Added subject requirement: {subject} at grade {req.min_grade_required}")
                # endfor
            # endif

            # Pattern 2: "A* in Mathematics A*/A in Physics" (Imperial style)
            # Look for patterns like "A* in Mathematics" or "A*/A in Physics"
            if " in " in text:
                # Split text into lines to process each requirement line
                lines = text.split('\n')
                for line in lines:
                    line = line.strip()

                    # Skip empty lines or lines without grade info
                    if not line or " in " not in line:
                        continue
                    # endif

                    # Look for grade followed by "in" followed by subject
                    words = line.split()
                    for i in range(len(words) - 2):
                        current_word = words[i]
                        next_word = words[i + 1]

                        # Check if current word is a grade and next word is "in"
                        is_grade = False
                        grade_chars = ["A", "B", "C", "D", "E", "*", "/"]
                        for char in current_word:
                            if char in grade_chars:
                                is_grade = True
                                break
                            # endif
                        # endfor

                        if is_grade and next_word.lower() == "in":
                            # Found "grade in" pattern, extract subject name
                            grade = current_word

                            # Get subject name (rest of the line or until parentheses/punctuation)
                            subject_words = []
                            for j in range(i + 2, len(words)):
                                word = words[j]

                                # Stop at punctuation or new grade patterns
                                if word.startswith("(") or word.startswith("[") or "." in word:
                                    break
                                # endif

                                # Stop if we hit another grade
                                is_new_grade = False
                                for char in word:
                                    if char in grade_chars and word != "A-levels":
                                        is_new_grade = True
                                        break
                                    # endif
                                # endfor

                                if is_new_grade:
                                    break
                                # endif

                                subject_words.append(word)
                            # endfor

                            if subject_words:
                                subject = " ".join(subject_words)
                                req.add_subject_requirement(subject, grade)
                                # print(f"Added subject requirement: {subject} at grade {grade}")
                            # endif
                        # endif
                    # endfor
                # endfor
            # endif
        # endif

        # Parse UCAS Tariff Points
        # Handle "UCAS Tariff - 112 - 128 points" or "UCAS Tariff - 72 points"
        # This regex finds UCAS tariff points.
        # - r'UCAS\s+Tariff\s*[-–]\s*' : Looks for "UCAS Tariff" followed by a hyphen.
        # - (\d+) : Finds the first number (the minimum points).
        # - (?:\s*[-–]\s*(\d+))? : Looks for an optional second number for ranges (e.g., "112 - 128").
        # - \s*points? : Allows for the word "points" at the end.
        ucas_pattern = r'UCAS\s+Tariff\s*[-–]\s*(\d+)(?:\s*[-–]\s*(\d+))?\s*points?'
        ucas_match = re.search(ucas_pattern, text, re.IGNORECASE)
        if ucas_match:
            # Use the minimum points (first number) for matching
            min_points_str = ucas_match.group(1)
            try:
                req.min_ucas_points = int(min_points_str)
                req.has_requirements = True
            except ValueError:
                pass
            # endtry
        # endif

        # Check if UCAS not accepted
        if "ucas tariff" in text_lower and "not accepted" in text_lower:
            req.accepts_ucas = False
            req.min_ucas_points = 0
        # endif

        # Parse BTEC requirements
        # Handle "BTEC ... - DDM - DMM" or "BTEC ... - MMP" or "BTEC ... - Not accepted"
        if "btec" in text_lower and "not accepted" in text_lower:
            # BTEC not accepted for this course
            pass
        else:
            btec_pattern = r'BTEC.*?[-–]\s*([D*MP]+)(?:\s*[-–]\s*([D*MP]+))?'
            btec_match = re.search(btec_pattern, text, re.IGNORECASE)
            if btec_match:
                # Use the minimum BTEC grade (first one) for matching
                btec_grades = btec_match.group(1).strip().upper()
                req.btec_grades = btec_grades
                req.has_requirements = True

                # Calculate UCAS points for BTEC
                btec_points = EntryRequirement.calculate_btec_points(btec_grades)
                if btec_points > 0:
                    if req.min_ucas_points == 0:
                        req.min_ucas_points = btec_points
                    else:
                        # Take the lower points
                        req.min_ucas_points = min(req.min_ucas_points, btec_points)
                    # endif
                # endif
            # endif
        # endif

        return req
    # enddef

# endclass

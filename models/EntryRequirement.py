import re

# UCAS Tariff Points mappings
A_LEVEL_POINTS = {
    'A*': 56,
    'A': 48,
    'B': 40,
    'C': 32,
    'D': 24,
    'E': 16
}

# BTEC grade values for calculation
BTEC_GRADE_VALUES = {
    'D*': 56,  # Distinction*
    'D': 48,   # Distinction
    'M': 32,   # Merit
    'P': 16    # Pass
}


class SubjectRequirement:
    """Class to hold subject-specific requirements"""
    def __init__(self, subject: str, grade: str):
        # Name of the subject (e.g., "Mathematics", "Physics")
        self.subject: str = subject
        
        # Grade needed for this subject
        self.grade: str = grade
    #enddef
    
    def to_dict(self) -> dict:
        return {"subject": self.subject, "grade": self.grade}
    # enddef
# endclass

class EntryRequirement:
    """
    Entry requirements class for university courses
    """
    
    def __init__(self):
        # Numeric points for database filtering
        self.min_ucas_points: int = 0
        
        # Minimum grade required per subject (e.g., "B" for BBB)
        self.min_grade_required: str = ""
        
        # Subject-specific requirements
        self.subject_requirements: list[SubjectRequirement] = []
        
        # BTEC grades
        self.btec_grades: str = ""
        
        # Display grades as text for the user
        self.display_grades: str = ""
        
        # If UCAS is accepted
        self.accepts_ucas: bool = True
        # If it has any requirements at all
        self.has_requirements: bool = True
    # enddef
    
    def add_subject_requirement(self, subject: str, grade: str) -> None:
        """Add a subject-specific requirement"""
        # Check if this subject already exists
        for req in self.subject_requirements:
            if req.subject.lower() == subject.lower():
                # Update existing requirement
                req.grade = grade
                return
        
        # Add new requirement
        self.subject_requirements.append(SubjectRequirement(subject, grade))
    # enddef
    
    def to_dict(self):
        """Convert to dictionary"""
        subject_reqs = []
        for req in self.subject_requirements:
            subject_reqs.append(req.to_dict())
        
        return {
            "min_ucas_points": self.min_ucas_points,
            "min_grade_required": self.min_grade_required,
            "subject_requirements": subject_reqs,
            "display_grades": self.display_grades,
            "btec_grades": self.btec_grades,
            "accepts_ucas": self.accepts_ucas,
            "has_requirements": self.has_requirements
        }
    # enddef
    
    def calculate_a_level_points(self, grades: str) -> int:
        """Calculate UCAS points from A-level grades"""
        if not grades:
            return 0
        #endif

        total_points = 0
        grades = grades.strip().upper()
        
        # Handle A* grades
        while 'A*' in grades:
            total_points += A_LEVEL_POINTS['A*']
            grades = grades.replace('A*', '', 1)
        #endwhile
        
        # Process remaining grades
        for grade in grades:
            if grade in A_LEVEL_POINTS:
                total_points += A_LEVEL_POINTS[grade]
            #endif
        #endfor
        
        return total_points
    # enddef
    
    def find_lowest_grade(self, grades: str) -> str:
        """Find the lowest grade in a grade string"""
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
        #endwhile
        
        # Check remaining grades
        for grade in grades:
            if grade in grade_order:
                grade_index = grade_order.index(grade)
                if grade_index > lowest_index:
                    lowest_grade = grade
                    lowest_index = grade_index
                #endif
            # endif
        #endfor
        
        return lowest_grade
    # enddef
    
    @staticmethod
    def calculate_btec_points(grades: str) -> int:
        """
        Calculate BTEC points from grade string

        For example:
        - "DDD" = 48 + 48 + 48 = 144
        - "DMM" = 48 + 32 + 32 = 112
        - "D*D*D*" = 56 + 56 + 56 = 168
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
        #endwhile
        
        # Process remaining single grades
        for grade in grades:
            if grade in BTEC_GRADE_VALUES:
                total += BTEC_GRADE_VALUES[grade]
            # endif
        #endfor
        
        return total
    # enddef
    
    @staticmethod
    def parse(requirement_text: str) -> 'EntryRequirement':
        """
        Parse entry requirement text from UCAS and create an EntryRequirement object
        
        Examples:
        - "A level - AAB"
        - "A level - BCC - BBB"
        - "UCAS Tariff - 120 points"
        - "A level - AAB including Mathematics at grade A"
        """
        req = EntryRequirement()
        
        if not requirement_text:
            req.has_requirements = False
            return req
        #endif
        
        text = requirement_text.strip()
        
        # Check for no requirements
        text_lower = text.lower()
        if "no formal" in text_lower or "no specific" in text_lower or "no requirement" in text_lower:
            req.has_requirements = False
            return req
        #endif
        
        # Parse A-level requirements
        a_level_pattern = r'A\s*level\s*[-–]\s*([A-Z*]{3,}(?:\s*[-–]\s*[A-Z*]{3,})?)'
        a_level_match = re.search(a_level_pattern, text, re.IGNORECASE)
        if a_level_match:
            grades = a_level_match.group(1).strip()
            req.display_grades = grades
            
            if "-" in grades:
                # Range like "BCC-BBB" - use minimum
                parts = grades.split("-")
                if len(parts) == 2:
                    min_grades = parts[0].strip()
                    req.min_ucas_points = req.calculate_a_level_points(min_grades)
                    req.min_grade_required = req.find_lowest_grade(min_grades)
                #endif
            else:
                # Single grade like "AAB"
                req.min_ucas_points = req.calculate_a_level_points(grades)
                req.min_grade_required = req.find_lowest_grade(grades)
            
            # Check for subject requirements
            subject_pattern = r'including\s+([A-Za-z]+(?:\s+[A-Za-z]+)?)\s+at\s+grade\s+([A-Z*])'
            subject_matches = re.findall(subject_pattern, text, re.IGNORECASE)
            for match in subject_matches:
                subject = match[0].strip()
                grade = match[1].strip()
                req.add_subject_requirement(subject, grade)
            #endfor
            
            # If no specific grade mentioned, check for just "including [subject]"
            if len(subject_matches) == 0:
                including_pattern = r'including\s+([A-Za-z]+(?:\s+[A-Za-z]+)?)'
                including_match = re.search(including_pattern, text, re.IGNORECASE)
                if including_match:
                    subject = including_match.group(1).strip()
                    req.add_subject_requirement(subject, "A")  # Default to A
                #endif
            #endif
        #endif
        
        # Parse UCAS Tariff Points
        # Handle "UCAS Tariff - 112 - 128 points" or "UCAS Tariff - 72 points"
        ucas_pattern = r'UCAS\s+Tariff\s*[-–]\s*(\d+)(?:\s*[-–]\s*(\d+))?\s*points?'
        ucas_match = re.search(ucas_pattern, text, re.IGNORECASE)
        if ucas_match:
            # Use the minimum points (first number) for matching
            min_points_str = ucas_match.group(1)
            try:
                req.min_ucas_points = int(min_points_str)
            except ValueError:
                pass
            #endtry
        #endif
        
        # Check if UCAS not accepted
        if "ucas tariff" in text_lower and "not accepted" in text_lower:
            req.accepts_ucas = False
            req.min_ucas_points = 0
        #endif
        
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
                
                # Calculate UCAS points for BTEC
                btec_points = EntryRequirement.calculate_btec_points(btec_grades)
                if btec_points > 0:
                    if req.min_ucas_points == 0:
                        req.min_ucas_points = btec_points
                    else:
                        # Take the lower points
                        req.min_ucas_points = min(req.min_ucas_points, btec_points)
                    #endif
                #endif
            #endif
        #endif
        
        return req
    # enddef
    
# endclass
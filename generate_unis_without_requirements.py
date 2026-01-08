#!/usr/bin/env python3

import json
from pathlib import Path


def has_any_requirements(courses: list[dict]) -> bool:
    """
    Checks whether any course in the list has entry requirements.

    :param courses: List of course dictionaries from the JSON file
    :return: True if any course has requirements, otherwise False
    """
    for course in courses:
        requirements = course.get("requirements")
        if requirements is None:
            requirements = []
        # endif
        for req in requirements:
            if not isinstance(req, dict):
                continue
            # endif
            has_requirements = req.get("has_requirements")
            min_points = req.get("min_ucas_points")
            display_grades = req.get("display_grades")
            if min_points is None:
                min_points = 0
            # endif
            if has_requirements or min_points > 0 or display_grades:
                return True
            # endif
        # endfor
    # endfor
    return False


# enddef


def main() -> None:
    """
    Reads the scraped JSON and writes a list of university names without requirements.

    :return: None
    """
    input_path = Path("universities.json")
    output_path = Path("unis_without_requirements.txt")

    data = json.loads(input_path.read_text())

    missing = []
    for uni in data:
        if not isinstance(uni, dict):
            continue
        # endif
        name_value = uni.get("name")
        if name_value is None:
            name_value = ""
        # endif
        name = name_value.strip()
        if not name:
            continue
        # endif
        courses = uni.get("courses")
        if courses is None:
            courses = []
        # endif
        if not has_any_requirements(courses):
            missing.append(name)
        # endif
    # endfor

    output_path.write_text("\n".join(missing))
    print(f"Wrote {len(missing)} university names to {output_path}")


# enddef


if __name__ == "__main__":
    main()

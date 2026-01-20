import json
from models.University import University


def save_json(universities: [University]):
    """
    Saves universities as JSON file.

    :param universities: List of University objects to save
    :return: None
    """

    university_json: [dict] = []

    for uni in universities:
        university_json.append(uni.to_dict())
    # endfor

    with open("universities.json", "w", encoding="utf-8") as f:
        json.dump(university_json, f, indent=2)
    # endwith
# enddef

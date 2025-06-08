import json
from models.University import *
from models.Course import *

def save_json(universities: [University]):
    """
    Saves universities as JSON file
    """

    university_json: [dict] = []

    for uni in universities:
        university_json.append(uni.to_json())
    #endfor

    with open("universities.json", "w", encoding="utf-8") as f:
        json.dump(university_json, f, indent=2)
    #endwith
#enddef
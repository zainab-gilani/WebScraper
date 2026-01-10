# Function Documentation - WebScraper Project

This document contains a table of all functions in the WebScraper project, including their names, arguments, process
descriptions, and return values.

## Table of Contents

- [JSONWriter Module](#jsonwriter-module)
- [Network Helper Module](#network-helper-module)
- [Scrape Search Results Module](#scrape-search-results-module)
- [Generate Unis Without Requirements Module](#generate-unis-without-requirements-module)
- [University Class](#university-class)
- [Course Class](#course-class)
- [EntryRequirement Class](#entryrequirement-class)

---

## JSONWriter Module

**File:** `JSONWriter.py`

| Function Name | Arguments Supplied         | Process                                                                                                                                                              | Returns |
|---------------|----------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|
| `save_json`   | List of University objects | Saves universities as JSON file by converting each University object to a dictionary and writing to "universities.json" with UTF-8 encoding and 2-space indentation. | Nothing |

---

## Network Helper Module

**File:** `network_helper.py`

| Function Name    | Arguments Supplied                                                                                                                                                           | Process                                                                                                                                                                                               | Returns                                                 |
|------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------|
| `log_failed_url` | URL that failed, short reason                                                                                                                                                | Saves failed URLs and the reason in a text file so they can be retried later.                                                                                                                         | Nothing                                                 |
| `get_with_retry` | URL to fetch, request headers, maximum number of retry attempts (default 3), seconds to wait between retries (default 10), optional session, timeout tuple (default (5, 15)) | Makes a GET request with retry logic for network failures. Adds a small delay per request. If the site blocks or the network fails, waits longer and tries again. Logs failures to `failed_urls.txt`. | Response object if successful, None if all retries fail |

---

## Scrape Search Results Module

**File:** `scrape_search_results.py`

| Function Name        | Arguments Supplied               | Process                                                                                                                                                                                                                      | Returns                               |
|----------------------|----------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------|
| `get_links_to_crawl` | Search link URL, request headers | Visits search link, counts the total number of search result pages by finding the pagination "last page" link, builds a list of all search links to crawl, and inserts the main search link as well for the caller to crawl. | List of all result page URLs to crawl |

---

## Scraper Module

**File:** `scraper.py`

| Function Name                | Arguments Supplied                                                  | Process                                                                                                                                 | Returns                                                                   |
|------------------------------|---------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------|
| `load_existing_universities` | JSON file path                                                      | Loads any universities already saved so the scraper can resume. Also counts how many saved universities have entry requirements vs not. | The saved university list, the saved university names, and the two counts |
| `load_target_universities`   | Text file path                                                      | Loads a newline-delimited list of university names to target for rescraping.                                                            | Set of university names                                                   |
| `replace_university`         | Existing list of university dictionaries, new university dictionary | Removes any existing entry with the same name and appends the new university data.                                                      | Updated list of university dictionaries                                   |
| `save_progress`              | JSON file path, list of university dictionaries                     | Saves the current scraped data so progress is not lost.                                                                                 | Nothing                                                                   |

---

## Generate Unis Without Requirements Module

**File:** `generate_unis_without_requirements.py`

| Function Name          | Arguments Supplied          | Process                                                                                                                                                   | Returns                                         |
|------------------------|-----------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------|
| `has_any_requirements` | List of course dictionaries | Checks if any course has real requirements by inspecting requirement flags, UCAS points, or display grades.                                               | True if any requirements exist, otherwise False |
| `main`                 | None                        | Reads `universities.json`, collects universities with no requirements, and writes their names to `unis_without_requirements.txt` for targeted rescraping. | Nothing                                         |

---

## University Class

**File:** `models/University.py`

| Function Name   | Arguments Supplied | Process                                                                                                                                                                                                                                                                              | Returns                                          |
|-----------------|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------|
| `__init__`      | None               | Initializes a new University object with empty name, location, link, link_all_courses, and an empty list of courses.                                                                                                                                                                 | Nothing                                          |
| `print`         | None               | Prints the university name, location, and link to the console.                                                                                                                                                                                                                       | Nothing                                          |
| `fetch_courses` | Request headers    | Obtains all links to all courses by getting all course result pages. Visits each course page and scrapes course details including name, link, course type, duration, mode, location, start date, and UCAS points. Creates Course objects and fetches detailed requirements for each. | Nothing                                          |
| `to_dict`       | None               | Turns the university into a simple format that can be saved to JSON, including its details and all of its courses.                                                                                                                                                                   | Dictionary containing all university information |

---

## Course Class

**File:** `models/Course.py`

| Function Name           | Arguments Supplied | Process                                                                                                                                                                                                                                                                                                                                              | Returns                                      |
|-------------------------|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------|
| `__init__`              | None               | Initializes a Course object to store information about a single university course including name, course type, duration, mode, location, start date, link, and an empty requirements list.                                                                                                                                                           | Nothing                                      |
| `print`                 | None               | Prints the course link and entry requirements to the console.                                                                                                                                                                                                                                                                                        | Nothing                                      |
| `fetch_requirements`    | Request headers    | Visits the specific webpage for this course to get the entry requirements. Checks for different HTML structures like options-bar divs or tables. Searches for accordion labels and requirement sections containing A level, UCAS, or BTEC information. Combines requirement texts and parses them into a single EntryRequirement (if any are found). | Nothing                                      |
| `clean_up_requirements` | None               | Removes empty requirements if real ones exist. Checks if any requirements have has_requirements set to True, and if so, filters out requirements without actual data.                                                                                                                                                                                | Nothing                                      |
| `to_dict`               | None               | Turns the course into a simple format that can be saved to JSON, including its details and entry requirements.                                                                                                                                                                                                                                       | Dictionary containing all course information |

---

## EntryRequirement Class

**File:** `models/EntryRequirement.py`

### SubjectRequirement Class

| Function Name | Arguments Supplied                                                                                                 | Process                                                                                              | Returns                           |
|---------------|--------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------|-----------------------------------|
| `__init__`    | The name of the subject (e.g., "Mathematics", "Physics"), the grade needed for this subject (e.g., "A", "B", "A*") | Creates a new subject requirement by storing the subject name and required grade.                    | Nothing                           |
| `to_dict`     | None                                                                                                               | Turns a subject requirement into a simple format that can be saved, with the subject name and grade. | Dictionary with subject and grade |

### EntryRequirement Methods

| Function Name              | Arguments Supplied                                                                 | Process                                                                                                                                                                                                                                                                                                               | Returns                                             |
|----------------------------|------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------|
| `__init__`                 | None                                                                               | Creates a new entry requirement object with default values including min_ucas_points, min_grade_required, subject_requirements list, btec_grades, display_grades, accepts_ucas flag, and has_requirements flag.                                                                                                       | Nothing                                             |
| `add_subject_requirement`  | The name of the subject (e.g., "Mathematics"), the grade required (e.g., "A", "B") | Adds a requirement for a specific subject to this course. If the subject already exists, updates the grade instead of adding a duplicate.                                                                                                                                                                             | Nothing                                             |
| `to_dict`                  | None                                                                               | Turns entry requirements into a simple format that can be saved, including points, grades, and subject rules.                                                                                                                                                                                                         | Dictionary containing all requirement information   |
| `calculate_a_level_points` | A string of A-level grades (e.g., "AAB", "A*AA", "BCC")                            | Calculates UCAS points from A-level grades by handling A* grades first, then processing remaining grades and looking up their point values.                                                                                                                                                                           | Total UCAS points for the grades                    |
| `find_lowest_grade`        | A string of A-level grades (e.g., "AAB", "BCC")                                    | Finds the lowest grade in a set of A-level grades by comparing each grade's position in the grade order (A*, A, B, C, D, E).                                                                                                                                                                                          | The lowest grade found (e.g., "B", "C")             |
| `calculate_btec_points`    | A string of BTEC grades (e.g., "DDD", "DMM", "D*D*D*")                             | Calculates BTEC points from grade string by handling D* grades first, then processing remaining grades (D, M, P) and summing their point values.                                                                                                                                                                      | Total UCAS points for the BTEC grades               |
| `clean_requirement_text`   | The raw requirement text from the website                                          | Cleans requirement text by removing extra whitespace; further edge cases are handled in `parse()`.                                                                                                                                                                                                                    | Cleaned text                                        |
| `parse`                    | The raw text from the UCAS website                                                 | Takes requirement text from UCAS and converts it into an EntryRequirement object. Parses A-level grades, UCAS tariff points, BTEC grades, and subject requirements using regex patterns and text analysis. Handles formats like "A level - AAB", "UCAS Tariff - 120 points", and "including Mathematics and Physics". | EntryRequirement object with all parsed information |

---

## Notes for NEA

### Key Features

1. **Retry Logic**: The `get_with_retry()` function handles network failures by waiting and retrying requests, which is
   essential when scraping multiple pages.

2. **Modular Design**: Functions are separated into different modules and classes to make the code reusable and easy to
   maintain.

3. **Robust Parsing**: The `parse()` function uses multiple regex patterns to handle inconsistent formatting across
   different university websites.

4. **Data Validation**: Functions like `clean_up_requirements()` ensure data quality by removing empty or invalid
   entries.

### Most Complex Functions

- **`parse()`** - Uses regex patterns and text analysis to extract structured data from unstructured text
- **`fetch_courses()`** - Processes multiple pages and course elements with network requests and HTML parsing
- **`fetch_requirements()`** - Handles different HTML structures with multiple fallback strategies

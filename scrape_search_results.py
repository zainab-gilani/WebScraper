import requests
import re
from bs4 import BeautifulSoup
from requests import Response
from network_helper import get_with_retry

def get_links_to_crawl(link, headers):
    """
    Visits search link, counts the total number of search result pages,
    builds a list of all search links to crawl, and inserts the main
    search link as well for the caller to crawl.

    :param link: The search URL to start from
    :param headers: Request headers dictionary
    :return: List of all result page URLs to crawl
    """

    # Store links to crawl as UCAS returns few results per page
    all_result_pages_to_crawl: [str] = []

    # 1. Visit main search page
    page: Response = get_with_retry(link, headers)
    
    # Check if the request failed
    if page is None:
        print(f"Failed to fetch {link}")
        return []
    #endif

    soup = BeautifulSoup(page.text, "html.parser")

    # 2. Get total page count of search results

    page_results = soup.find_all("ul", class_="pagination__list")
    
    total_pages = 0
    for page_result in page_results:
        result_items = page_result.find_all("li", class_="pagination__item")

        for result_item in result_items:
            result_links = result_item.find_all("a")

            for item in result_links:
                if item.has_attr("aria-label"):
                    page_label = item.attrs["aria-label"]

                    if "last page" in page_label.lower():
                        # Extract page number from the aria-label "Last Page, Page 21"
                        page_match = re.search(r"page\s+(\d+)", page_label.lower())
                        if page_match:
                            total_pages = int(page_match.group(1))
                        #endif
                    #endif
                #endif
            #endfor
        #endfor
    #endfor

    print(f"Total results for search: {total_pages}")

    # 3. Build links pages on total pages found in results that we will need to crawl

    for i in range(2, total_pages+1):
        next_page = f"{link}&page={i}"

        all_result_pages_to_crawl.append(next_page)
    #endfor

    # 4. We will re-visit this first page to scrape all universities from this page
    all_result_pages_to_crawl.insert(0, link)

    return all_result_pages_to_crawl
#enddef
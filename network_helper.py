import time
import requests
from requests import Response


def log_failed_url(url, reason):
    """
    Logs failed URLs so we can retry them later if needed.
    :param url: The URL that failed
    :param reason: Short reason for the failure
    :return: None
    """
    try:
        with open("failed_urls.txt", "a", encoding="utf-8") as f:
            f.write(f"{url} | {reason}\n")
        # endwith
    except Exception:
        # If logging fails, just ignore it
        pass
    # endtry


# enddef

def get_with_retry(url, headers, max_retries=3, wait_time=10, timeout=(5, 15)):
    """
    Makes a GET request with retry logic for network failures.

    :param url: The URL to fetch
    :param headers: Request headers dictionary
    :param max_retries: Maximum number of retry attempts (default 3)
    :param wait_time: Seconds to wait between retries (default 10)
    :return: Response object if successful, None if all retries fail
    """

    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)

            # If we got a non-OK response, treat as failure to keep data clean
            if response.status_code >= 400:
                print(f"Request failed with status {response.status_code} for {url}")
                log_failed_url(url, f"status {response.status_code}")
                response = None
            # endif

            # If we got here, the request succeeded
            if response is not None:
                return response
            # endif
        except Exception as e:
            # Network error occurred
            print(f"Network error on attempt {attempt + 1}: {e}")

            # Check if we should retry
            if attempt < max_retries - 1:
                print(f"Waiting {wait_time} seconds before retrying...")
                time.sleep(wait_time)
            else:
                print(f"Failed after {max_retries} attempts")
                log_failed_url(url, f"network error: {e}")
                return None
            # endif
        # endtry
    # endfor

    return None
# enddef

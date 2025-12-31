import time
import random
import requests
from requests import Response

_default_session = requests.Session()

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
        #endwith
    except Exception:
        # If logging fails, just ignore it
        pass
    #endtry
#enddef

def get_with_retry(url, headers, max_retries=3, wait_time=10, session=None, timeout=(5, 15)):
    """
    Makes a GET request with retry logic for network failures.

    :param url: The URL to fetch
    :param headers: Request headers dictionary
    :param max_retries: Maximum number of retry attempts (default 3)
    :param wait_time: Seconds to wait between retries (default 10)
    :return: Response object if successful, None if all retries fail
    """

    # Try to get the page and if it fails just try again if possible
    if session is None:
        session = _default_session
    #endif

    for attempt in range(max_retries):
        try:
            # Small polite delay so we don't hammer the site, but keep it fast
            sleep_duration = random.uniform(0.2, 0.6)
            time.sleep(sleep_duration)
            
            response = session.get(url, headers=headers, timeout=timeout)
            
            # Handle rate limiting or temporary blocks
            if response.status_code in [403, 429, 503]:
                print(f"Blocked or rate-limited (status {response.status_code}) on attempt {attempt + 1}")
                
                if attempt < max_retries - 1:
                    # Respect Retry-After if the server gives it
                    retry_after = response.headers.get("Retry-After")
                    if retry_after and retry_after.isdigit():
                        wait_time = int(retry_after)
                    else:
                        # Exponential backoff with jitter
                        wait_time = wait_time * (2 ** attempt)
                        wait_time += random.uniform(0.0, 1.0)
                    #endif
                    print(f"Waiting {wait_time} seconds before retrying...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"Failed after {max_retries} attempts")
                    log_failed_url(url, f"status {response.status_code} after retries")
                    return None
                #endif
            #endif
            
            # If we got a non-OK response, treat as failure to keep data clean
            if response.status_code >= 400:
                print(f"Request failed with status {response.status_code} for {url}")
                log_failed_url(url, f"status {response.status_code}")
                return None
            #endif
            
            # If we got here, the request succeeded
            return response
        except Exception as e:
            # Network error occurred
            print(f"Network error on attempt {attempt + 1}: {e}")
            
            # Check if we should retry
            if attempt < max_retries - 1:
                # Exponential backoff with jitter
                backoff_time = wait_time * (2 ** attempt)
                backoff_time += random.uniform(0.0, 1.0)
                print(f"Waiting {backoff_time} seconds before retrying...")

                time.sleep(backoff_time)
            else:
                print(f"Failed after {max_retries} attempts")
                log_failed_url(url, f"network error: {e}")
                return None
            #endif
        #endtry
    #endfor
    
    return None
#enddef

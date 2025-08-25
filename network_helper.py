import time
import requests
from requests import Response

def get_with_retry(url, headers, max_retries=3, wait_time=10):
    """
    Makes a GET request with retry logic for network failures
    
    :param url: The URL to fetch
    :param headers: Request headers
    :param max_retries: Maximum number of retry attempts
    :param wait_time: Seconds to wait between retries
    :return: Response object if successful, None if all retries fail
    """

    # Try to get the page and if it fails just try again if possible

    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers)

            # If we got here, the request succeeded
            return response
        except Exception as e:
            # Network error occurred
            print(f"Network error on attempt {attempt + 1}: {e}")
            
            # Check if we should retry
            if attempt < max_retries - 1:
                print(f"Waiting {wait_time} seconds before retrying...")

                time.sleep(wait_time)
            else:
                print(f"Failed after {max_retries} attempts")
                return None
            #endif
        #endtry
    #endfor
    
    return None
#enddef
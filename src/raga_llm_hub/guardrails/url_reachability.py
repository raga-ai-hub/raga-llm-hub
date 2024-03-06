from typing import List
from urllib import error, request

import requests

from .utils import extract_urls


class URLReachability:
    """
    This scanner checks URLs for their reachability.
    """

    def __init__(
        self,
        question,
        response,
        success_status_codes: List[int] = None,
        timeout: int = 5,
        threshold=0.5,
    ):
        """
        Initialize the test instance with the provided parameters.

        Args:
        - question: str, the question to be evaluated for contextual relevancy
        - response: str, the response for the question
        - success_status_codes: A list of status codes that are considered as successful.
        - threshold: int, The timeout in seconds for the HTTP requests (default 5)
        """
        self.question = question
        self.output = response

        if success_status_codes is None:
            success_status_codes = (200, 201, 202, 301, 302)

        self._success_status_codes = success_status_codes
        self._timeout = timeout
        self._threshold = threshold

    def is_reachable(self, url: str) -> bool:
        """
        Check if the URL is reachable.
        """
        if not (url.startswith("http://") or url.startswith("https://")):
            url = "https://" + url
        try:
            connection = request.urlopen(url, timeout=self._timeout)
            status_code = connection.getcode()
            connection.close()

            return status_code in self._success_status_codes
        except error.URLError:
            return False

    def run(self):
        urls = extract_urls(self.output)

        unreachable_urls = [url for url in urls if not self.is_reachable(url)]

        if len(urls) == 0:
            reason = "No URLs found!"
            score = 1.0
        elif len(unreachable_urls) == 0:
            reason = "No unreachable URLs found!"
            score = 1.0
        else:
            reason = "Unreachable URLS:\n"
            for i, url in enumerate(unreachable_urls):
                reason += f"{i}: {url}\n"
            score = (len(urls) - len(unreachable_urls)) / len(urls)

        result = {
            "prompt": self.question,
            "response": self.output,
            "score": score,
            "threshold": self._timeout,
            "is_passed": True if score > self._threshold else False,
            "reason": reason,
        }

        return result

"""
Shamelessly stolen from:
https://github.com/lukecyca/pyslack
"""
import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from horey.h_logger import get_logger
from horey.gemini_api.gemini_api_configuration_policy import (
    GeminiAPIConfigurationPolicy,
)

logger = get_logger()


class GeminiAPI:
    """
    Main Class.
    """

    def __init__(self, configuration: GeminiAPIConfigurationPolicy = None):
        self.configuration = configuration
        self.gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
        #self.gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

        self.session = requests.Session()

        # Configure retry strategy
        retries = Retry(
        total=6,                        # Retry up to 5 times
        backoff_factor=1,               # Wait 1s, 2s, 4s, 8s, 16s, 32s between retries
        status_forcelist=[500, 502, 503, 504], # Retry on these server errors
        raise_on_status=False
        )

        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("https://", adapter)


    @property
    def headers(self):
        """
        Construct request.

        @param request:
        @return:
        """
        
        return {"X-goog-api-key": self.configuration.api_key,
                    "Content-Type": "application/json"}

    def request_raw(self, text):
        """
        Send POST request

        @param text:
        @return:
        """
        data = {"contents": [
        {
            "parts": [
            {
                "text": text
            }
            ]
        }
        ]
        }

        response = self.session.post(self.gemini_url, headers=self.headers, json=data, timeout=30)
        response.raise_for_status()

        return response.json()

    def ask_json(self, text, json_format):
        """
        Request tesxt return response
        """
        prompt = f"{text}\n\nReturn a valid JSON object matching this schema:\n{json.dumps(json_format)}"
        
        response = self.request_raw(prompt)
        raw_text = response["candidates"][0]["content"]["parts"][0]["text"]
        clean_text = raw_text
        while True:
            for strip_me in "`\njson":
                clean_text = clean_text.strip(strip_me)
            if raw_text == clean_text:
                break
            raw_text = clean_text
        
        try:
            return json.loads(raw_text)
        except Exception:
            breakpoint()

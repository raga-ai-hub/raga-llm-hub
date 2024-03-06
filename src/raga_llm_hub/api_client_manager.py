"""
APIClientManager: Manage API keys for different sources
"""

import os

from openai import OpenAI


class APIClientManager:
    """Class for managing API keys for different sources"""

    def set_api_keys(self, api_keys):
        """
        Set the API keys for OpenAI and Hugging Face Hub.

        Parameters:
            api_keys (dict): A dictionary containing the API keys for OpenAI and Hugging Face Hub.

        Returns:
            None
        """
        open_ai_api_key = (
            api_keys.get("OPENAI_API_KEY")
            if api_keys and "OPENAI_API_KEY" in api_keys
            else os.getenv("OPENAI_API_KEY", None)
        )
        hugging_face_hub_api_token = (
            api_keys.get("HUGGINGFACEHUB_API_TOKEN")
            if api_keys and "HUGGINGFACEHUB_API_TOKEN" in api_keys
            else os.getenv("HUGGINGFACEHUB_API_TOKEN", None)
        )

        if open_ai_api_key:
            os.environ["OPENAI_API_KEY"] = open_ai_api_key

        if hugging_face_hub_api_token:
            os.environ["HUGGINGFACEHUB_API_TOKEN"] = hugging_face_hub_api_token

        os.environ["TOKENIZERS_PARALLELISM"] = "true"

    def set_openai_client(self):
        """
        Sets the OpenAI client using the OPENAI_API_KEY environment variable.

        Returns:
            OpenAI: The OpenAI client.

        Raises:
            ValueError: If the OPENAI_API_KEY environment variable is not set.
        """
        if os.getenv("OPENAI_API_KEY"):
            return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        raise ValueError("OPENAI_API_KEY needs to be set.")

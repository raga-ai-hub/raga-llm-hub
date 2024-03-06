"""
Main Function for RagaLLMEval
"""

import os
from pathlib import Path

from .api_client_manager import APIClientManager
from .observer.raga_observer import call_openai_service
from .track_manager import TrackManager
from .utils.utils import generate_unique_name


class RagaLLMObserver(TrackManager, APIClientManager):
    """
    Main class for RagaLLMObserver
    """

    def __init__(self, api_keys=None, observer_name=None):
        """
        Initialize the API client with the given API keys and evaluation name.

        Parameters:
            api_keys (dict): API keys for authentication.
            eval_name (str): Name of the evaluation.

        Returns:
            None
        """
        # Set the configuration
        APIClientManager.__init__(self)
        self.set_api_keys(api_keys=api_keys)
        self._openai_client = self.set_openai_client()

        # Initialise the Managers
        self.observer_name = observer_name if observer_name else generate_unique_name()
        TrackManager.__init__(
            self, self.__get_db_path("raga_llm_tracing.db"), observer_name
        )

        self._metrics_to_track = []

        self.__print_welcome_message()

    def __print_welcome_message(self):
        print("🌟 Welcome to raga_llm_hub! 🌟")
        print(
            "The most comprehensive LLM (Large Language Models) testing library at your service.\n"
        )
        print(f"Launching Evaluation: '{self.observer_name}'")
        print("Keep this identifier handy for tracking your progress!\n")

    def __get_db_path(self, db_filename):
        # For Unix-like systems, place in a hidden directory in the user's home directory
        # For Windows, use the AppData directory
        if os.name == "posix":  # Unix-like
            hidden_dir = Path.home() / ".raga_llm_tracing"
        else:  # Windows
            hidden_dir = Path(os.getenv("APPDATA")) / "RagaLLMEval"

        # Ensure the directory exists
        hidden_dir.mkdir(parents=True, exist_ok=True)
        print("File Location", str(hidden_dir / db_filename))
        return str(hidden_dir / db_filename)

    def load_trace(self, tracer_name):
        """
        Load and evaluate the given tracer_name, and set the final results.

        :param tracer_name: The name of the tracer.
        :return: The current instance of the object.
        """
        self._final_results = self.__load_previous_eval(tracer_name)

        return self

    def get_results(self):
        """
        This function returns the final results. If there are no results, it raises a ValueError.
        """
        if not self._final_results:
            raise ValueError("🚫 No results to return.")

        return self._final_results

    def call_default_tracer(self, prompt):
        response = call_openai_service(self, prompt)
        return response

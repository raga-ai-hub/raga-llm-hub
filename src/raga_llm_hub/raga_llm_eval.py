"""
Main Function for RagaLLMEval
"""

import os
from pathlib import Path

from .api_client_manager import APIClientManager
from .db_manager import DBManager
from .result_manager import ResultManager
from .test_manager import TestManager
from .utils.utils import generate_unique_name


class RagaLLMEval(DBManager, APIClientManager, TestManager, ResultManager):
    """
    Main class for RagaLLMEval
    """

    def __init__(self, api_keys=None, eval_name=None):
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
        ResultManager.__init__(self)
        TestManager.__init__(self, self._openai_client)
        DBManager.__init__(self, self.__get_db_path("raga_llm_hub.db"))

        self._final_results = []
        self._tests_to_execute = []
        self.eval_name = eval_name if eval_name else generate_unique_name()

        self.__print_welcome_message()

    def __print_welcome_message(self):
        print("🌟 Welcome to RagaLLMHub! 🌟")
        print(
            "The most comprehensive LLM (Large Language Models) testing library at your service.\n"
        )
        print(f"Launching Evaluation: '{self.eval_name}'")
        print("Keep this identifier handy for tracking your progress!\n")

    def __get_db_path(self, db_filename):
        # For Unix-like systems, place in a hidden directory in the user's home directory
        # For Windows, use the AppData directory
        if os.name == "posix":  # Unix-like
            hidden_dir = Path.home() / ".raga_llm_hub"
        else:  # Windows
            hidden_dir = Path(os.getenv("APPDATA")) / "RagaLLMEval"

        # Ensure the directory exists
        hidden_dir.mkdir(parents=True, exist_ok=True)

        return str(hidden_dir / db_filename)

    def load_eval(self, eval_name):
        """
        Load and evaluate the given eval_name, and set the final results.

        :param eval_name: The name of the evaluation.
        :return: The current instance of the object.
        """
        self._final_results = self.__load_previous_eval(eval_name)

        return self

    def add_test(self, data=None, test_names=None, test_category=None, arguments=None):
        """
        Add a test to the test suite with the given data, test names, test category, and arguments.

        Args:
            data: The data for the test.
            test_names: Optional; a list of test names.
            test_category: Optional; the category of the test.
            arguments: Optional; additional arguments for the test.

        Returns:
            self: The modified object with the added test.
        """
        # if the test name is a string, convert it to a list
        if isinstance(test_names, str):
            test_names = [test_names]

        self._tests_to_execute.extend(
            self._add_test(data, test_names, test_category, arguments)
        )

        return self

    def _clear_added_tests(self):
        """
        Clear the list of tests to be executed.
        """
        self._tests_to_execute = []

    def run(self):
        """
        Run the tests, save run details, and return the current object.
        """
        try:
            self._final_results = self._run(
                self._tests_to_execute, eval_id=self.eval_name
            )
        except Exception as _:
            print("🚫 Error while running the tests. Resetting...")
            self._clear_added_tests()

        # Save run details
        self.save_run_details(
            eval_name=self.eval_name, final_results=self._final_results
        )

        # Flush the tests to be executed
        self._clear_added_tests()

    def get_results(self):
        """
        This function returns the final results. If there are no results, it raises a ValueError.
        """
        if not self._final_results:
            raise ValueError("🚫 No results to return.")

        return self._final_results

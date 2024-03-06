"""
Main Module for LLM Test Execution
"""

import requests

from .observer.raga_observer import raga_observer
from .raga_llm_eval import RagaLLMEval
from .raga_llm_observer import RagaLLMObserver
from .tests.test_data import get_data
from .tests.test_executor import TestExecutor
from .ui.app import launch_app

__all__ = [
    "RagaLLMEval",
    "RagaLLMObserver",
    "TestExecutor",
    "get_data",
    "raga_observer",
    "launch_app",
]

__version__ = "1.0.0.10"


def check_latest_version(package_name):
    """
    Check the latest version of the package on PyPI and inform the user if an update is available.
    """
    try:
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=3)
        response.raise_for_status()
        latest_version = response.json()["info"]["version"]
        if __version__ != latest_version:
            print(
                f"Update available for {package_name} package. Your version: {__version__}. Latest version: {latest_version}."
            )
            print(
                f"Run 'pip install --upgrade raga_llm_hub=={latest_version}' to update to the latest version."
            )
    except Exception as e:
        print("Failed to check the latest package version:", e)


# Check the latest version
check_latest_version("raga_llm_hub")

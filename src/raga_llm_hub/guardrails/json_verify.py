import json
import re

import json_repair
import regex

JSON_PATTERN = r"(?<!\\)(?:\\\\)*\{(?:[^{}]|(?R))*\}"


class JSONVerify:
    """
    A scanner class to detect, validate and repair JSON structures within a given output.

    It primarily serves to detect JSON objects and arrays using regular expressions,
    then to validate them to ensure their correctness and finally to repair them if necessary.
    """

    def __init__(self, prompt, response, repair: bool = True):
        """Initialize the JSON scanner.

        Parameters:
            that should be present. Defaults to 0.
            repair (bool, optional): Whether to repair the broken JSON. Defaults to False.
        """

        self.prompt = prompt
        self.response = response
        self._repair = repair
        self._pattern = regex.compile(JSON_PATTERN, re.DOTALL)

    @staticmethod
    def is_valid_json(json_str: str) -> bool:
        """Check if the input string is a valid JSON.

        Parameters:
            json_str (str): The input string to check.

        Returns:
            bool: True if the input string is a valid JSON, False otherwise.
        """
        try:
            json.loads(json_str)
            return True
        except ValueError as e:
            print("Invalid JSON")
            return False

    @staticmethod
    def repair_json(json_str: str) -> str:
        """Repair a broken JSON string.

        Parameters:
            json_str (str): The input string to repair.

        Returns:
            str: The repaired JSON string.
        """
        try:
            repaired_json = json_repair.repair_json(
                json_str, skip_json_loads=True, return_objects=False
            )
        except ValueError:
            return json_str

        return repaired_json

    def run(self):
        sanitized_prompt = self.response
        result = {
            "prompt": self.prompt,
            "response": self.response,
        }

        if self.prompt.strip() == "":
            result["sanitized_prompt"] = sanitized_prompt
            result["is_passed"] = True
            result["score"] = 1.0
            return result

        # Find JSON object and array candidates using regular expressions
        json_candidates = self._pattern.findall(self.response)

        # Validate each JSON
        for json_candidate in json_candidates:
            if self.is_valid_json(json_candidate):
                result["is_passed"] = "True"
                result["score"] = 1.0
            else:
                result["is_passed"] = "Failed"
                result["score"] = 0.0

                if self._repair:
                    print("Found invalid JSON. Trying to repair it...")

                    repaired_json = self.repair_json(json_candidate)
                    if not self.is_valid_json(repaired_json):
                        print(f"Could not repair JSON. Skipping...")

                        continue

                    sanitized_prompt = repaired_json

        result["sanitized_prompt"] = sanitized_prompt
        return result

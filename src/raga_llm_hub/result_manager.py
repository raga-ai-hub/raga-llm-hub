"""
ResultManager: Manage the results of the evaluation including printing, saving to file etc.
"""

import json

from prettytable import ALL, PrettyTable

from .utils.utils import NumpyEncoder


class ResultManager:
    def __init__(self):
        self._results = []
        self._final_results = []
        self._output_format = "summary"

    def print_results(self):
        """
        A method to print the results in a pretty table format, creating a separate table for each test type,
        and mapping internal key names to user-friendly column names for display.
        """

        if not self._final_results:
            raise ValueError("🚫 No results to print.")

        # Mapping of internal key names to display names
        key_name_mapping = {
            "test_name": "Test Name",
            "probe_name": "Probe Name",
            "prompt": "Prompt",
            "response": "Response",
            "evaluated_with": "Parameters",
            "score": "Score",
            "is_passed": "Result",
            "reason": "Reason",
            "threshold": "Threshold",
            "context": "Context",
            "concept_set": "Concept Set",
            "cost": "Cost",
            "latency": "Latency",
            "test_arguments": "Test Arguments",
            "expected_response": "Expected Response",
            "sanitized_prompt": "Sanitized Prompt",
            "sanitized_response": "Sanitized Response",
            "failed_case_prompt": "failed_case_prompt",
            "failed_case_response": "failed_case_response",
            "detectors_score": "Detectors Scores",
        }

        print("""\n📊 Results:""")

        # Group data by test names
        test_groups = {}
        for test_data in self._final_results:
            test_name = test_data.get("test_name", "Unknown Test Name")
            if test_name not in test_groups:
                test_groups[test_name] = []
            test_groups[test_name].append(test_data)

        # Iterate over each test group and create a table
        for test_name, test_datas in test_groups.items():
            print(f"\nTest Name: {test_name}\n")

            # Determine keys actually used in test_datas
            used_keys = set()
            for test_data in test_datas:
                used_keys.update(test_data.keys())

            if "note" in used_keys:
                print(
                    f"\nNote: Only sample internal prompt and model response for 'failed cases' is being displayed. Use 'evaluator.save_results('results.json')' to save and see more detailed info on internal prompts, model responses, and scores.\n"
                )

            # Preserve order of keys as in key_name_mapping but filter out unused keys
            field_names = [
                display_name
                for key, display_name in key_name_mapping.items()
                if key in used_keys
            ]

            table = PrettyTable()
            table.field_names = field_names

            # pylint: disable=protected-access
            table._max_width = {name: 25 for name in field_names}
            table.hrules = ALL

            for test_data in test_datas:
                row = []
                for key in key_name_mapping:  # Ensure order and filter used keys
                    if key in used_keys:
                        value = test_data.get(key, "")

                        if isinstance(value, bool):
                            row.append("✅" if value else "❌")
                        elif isinstance(value, (int, float)):
                            row.append(f"{value:.2f}")
                        elif (
                            key == "evaluated_with"
                        ):  # Special formatting for evaluated_with
                            value = ", ".join([f"{k}: {v}" for k, v in value.items()])
                            row.append(value)
                        else:
                            row.append(value)
                table.add_row(row)

            print(table)

        print()

    def save_results(self, file_path):
        """
        Save the results to a specified file in JSON format.

        Args:
            file_path (str): The path to the file where the results will be saved.

        Returns:
            None
        """
        if not self._final_results:
            raise ValueError("🚫 No results to save.")

        # Convert the results dictionary to a JSON string using the custom encoder

        results_json = json.dumps(self._final_results, indent=4, cls=NumpyEncoder)

        # Write the JSON string to the specified fi
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(results_json)

        print(f"Results saved to {file_path}")

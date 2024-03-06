import csv
import sys
from io import StringIO


class ValidCsv:
    """
    ValidCsv checks whether input is in correct csv format or not.
    """

    def __init__(
        self,
        prompt,
    ):
        """
        Initializes the ValidCsv class.

        Args:
        - prompt: str, the text to be evaluated for ValidCsv.
        """
        self.prompt = prompt

    def run(self):
        res = ""
        try:
            # Split the text by newline characters
            lines = self.prompt.strip().split("\n")
            if lines != []:
                # Extract header and data separately
                header = lines[0]
                data_lines = lines[1:]

                # Join data lines back together
                trimmed_data = "\n".join(data_lines)

                # Reconstruct data with header
                self.prompt = "\n".join([header, trimmed_data])
            reader = csv.DictReader(StringIO(self.prompt))
            header = reader.fieldnames
            # Check that field names do not contain spaces
            if any(" " in name for name in header):
                res = False

            # Check that all rows have the same number of fields as the header
            for row in reader:
                if len(row) != len(header):
                    res = False
                    break

            # Check that no values are missing
            for row in reader:
                if None in row.values():
                    res = False
                    break
            if res == "":
                res = True
        except csv.Error:
            res = False
        result = {
            "prompt": self.prompt,
            "is_passed": res,
        }

        return result

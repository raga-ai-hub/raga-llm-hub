import ast
import re


class ValidPython:
    """
    A scanner class to validate python code within a given output.

    It primarily serves to detect python code blocks using regular expressions,
    then to validate them to ensure their syntactic structure.
    """

    def __init__(self, prompt, response):
        """Initialize the Python scanner."""
        self.prompt = prompt
        self.response = response

    def extract_python(self):
        pattern = r"```python(.*?)```"
        match = re.search(pattern, self.response, re.DOTALL)
        if match:
            return match.group(1).strip()
        else:
            return None

    def validate_python(self, code):
        try:
            ast.parse(code)
        except SyntaxError as e:
            return e.msg

        return 1

    def run(self):
        python_code = self.extract_python()
        is_valid = self.validate_python(python_code)
        if is_valid == 1:
            score = 1
        else:
            score = 0

        result = {
            "prompt": self.prompt,
            "response": self.response,
            "is_passed": True if score else False,
            "score": score,
            "evaluated_with": {
                "include_reason": is_valid if score == 0 else "No syntax Error",
            },
        }

        return result

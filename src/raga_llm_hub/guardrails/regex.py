import re
from enum import Enum
from typing import Pattern, Sequence, Union

from presidio_anonymizer.core.text_replace_builder import TextReplaceBuilder


class MatchType(Enum):
    SEARCH = "search"
    FULL_MATCH = "fullmatch"

    def match(self, pattern: Pattern[str], text: str):
        return getattr(pattern, self.value)(text)


class Regex:
    """
    A class used to detect patterns in the output of a language model using regular expressions.

    This class relies on the list of regular expressions provided by the user. If any of the patterns
    matches the output, the output is considered invalid. It is also possible to redact the output.
    """

    def __init__(
        self,
        prompt: str,
        patterns: Sequence[str],
        is_blocked: bool = True,
        match_type: Union[MatchType, str] = MatchType.SEARCH,
        redact: bool = True,
    ):
        """
        Initializes an instance of the Regex class.

        Parameters:
            prompt (str): The prompt to scan for regex patterns.
            patterns (Sequence[str]): A list of regular expressions to use for pattern matching.
            is_blocked (bool): Whether the patterns are blocked or allowed.
            match_type (str): The type of match to use. Can be either "search" or "fullmatch".
            redact (bool): Whether to redact the output or not.

        Raises:
            ValueError: If no patterns provided or both good and bad patterns provided.
        """
        if isinstance(match_type, str):
            match_type = MatchType(match_type)

        try:
            self._patterns = [re.compile(pattern) for pattern in patterns]
        except re.error:
            print("Non valid regex pattern")
            exit()

        self._prompt = prompt
        # self._patterns = [re.compile(pattern) for pattern in patterns]
        self._match_type = match_type
        self._is_blocked = is_blocked
        self._redact = redact

    def run(self) -> dict:
        result = {
            "prompt": self._prompt,
            "reason": "No pattern matched",
            "is_passed": True,
            "score": 0.0,
            "sanitized_prompt": self._prompt,
            "evaluated_with": {
                "patterns": [pattern.pattern for pattern in self._patterns],
                "match_type": self._match_type.value,
                "redact": self._redact,
            },
        }
        # text_replace_builder = TextReplaceBuilder(original_text=self._prompt)

        updated_prompt = self._prompt
        pattern_matched = False
        for pattern in self._patterns:
            text_replace_builder = TextReplaceBuilder(original_text=updated_prompt)

            match = self._match_type.match(pattern, self._prompt)
            if match is not None:
                pattern_matched = True
                if self._is_blocked:
                    if self._redact:
                        text_replace_builder.replace_text_get_insertion_index(
                            "[REDACTED]",
                            match.start(),
                            match.end(),
                        )
                        updated_prompt = text_replace_builder.output_text
                else:
                    result["reason"] = "Pattern matched the text"
                    result["is_passed"] = True
                    return result

        if pattern_matched:
            result["reason"] = "Patterns were detected in the text"
            result["is_passed"] = False
            result["score"] = 1.0
            result["sanitized_prompt"] = text_replace_builder.output_text
        else:
            if self._is_blocked:
                result["reason"] = "None of the patterns were found in the text"
                result["is_passed"] = True
                return result
            else:
                result["reason"] = "None of the patterns matched the text"
                result["is_passed"] = False
                result["score"] = 1.0
        return result

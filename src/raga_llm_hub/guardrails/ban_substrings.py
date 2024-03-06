import os
import re
from enum import Enum
from typing import Sequence, Union

stop_file_path = "resources/prompt_stop_substrings.json"


class MatchType(Enum):
    STR = "str"
    WORD = "word"

    def match(self, text: str, substring: str) -> bool:
        if self == MatchType.STR:
            return substring in text

        if self == MatchType.WORD:
            return re.search(r"\b" + substring + r"\b", text) is not None


class BanSubstrings:
    """
    BanSubstrings class is used to ban certain substrings from appearing in the prompt.

    The match can be done either at a string level or word level.
    """

    def __init__(
        self,
        prompt: str,
        substrings: Sequence[str],
        match_type: Union[MatchType, str] = MatchType.STR,
        case_sensitive: bool = False,
        redact: bool = True,
        contains_all: bool = False,  # contains any
    ):
        """
        Initialize BanSubstrings object.

        Parameters:
            prompt (str): Prompt to check for banned substrings.
            substrings (Sequence[str]): List of substrings to ban.
            match_type (str): Type of match to perform. Can be either 'str' or 'word'. Default is 'str'.
            case_sensitive (bool, optional): Flag to indicate if the match should be case-sensitive. Default is False.
            redact (bool, optional): Flag to indicate if the banned substrings should be redacted. Default is False.
            contains_all (bool): Flag to indicate if need to match all substrings instead of any of them. Default is contains any.

        Raises:
            ValueError: If no substrings are provided or match_type is not 'str' or 'word'.
        """
        if isinstance(match_type, str):
            match_type = MatchType(match_type)

        self._prompt = prompt
        self._match_type = match_type
        self._case_sensitive = case_sensitive
        self._substrings = substrings
        self._redact = redact
        self._contains_all = contains_all

    @staticmethod
    def _redact_text(text: str, substrings: Sequence[str]) -> str:
        redacted_text = text
        for s in substrings:
            regex = re.compile(r"\b" + re.escape(s) + r"\b", re.IGNORECASE)
            redacted_text = regex.sub("[REDACTED]", redacted_text)
        return redacted_text

    def run(self) -> dict:
        result = {
            "prompt": self._prompt,
            "is_passed": True,
            "reason": "No banned substrings found in prompt.",
            "score": 0.0,  # Initializing score as 0.0
            "evaluated_with": {
                "substrings": self._substrings,
                "match_type": self._match_type.value,
                "redact": self._redact,
            },
        }

        sanitized_prompt = self._prompt
        matched_substrings = []
        missing_substrings = []

        for s in self._substrings:
            if self._case_sensitive is False:
                s, prompt = s.lower(), self._prompt.lower()
            if self._match_type.match(prompt, s):
                matched_substrings.append(s)
            else:
                missing_substrings.append(s)

        if self._contains_all:
            if len(missing_substrings) > 0:
                result["reason"] = "Not all banned substrings found in prompt."
                result["is_passed"] = False
                return result

            if self._redact:
                sanitized_prompt = self._redact_text(
                    sanitized_prompt, matched_substrings
                )
                result["sanitized_prompt"] = sanitized_prompt

            result["score"] = 1.0
            result["is_passed"] = False
            result["reason"] = "All banned substrings found in prompt."
            return result

        if matched_substrings:
            result["reason"] = "Banned substrings found in prompt."
            result["is_passed"] = False

            if self._redact:
                sanitized_prompt = self._redact_text(
                    sanitized_prompt, matched_substrings
                )
                result["sanitized_prompt"] = sanitized_prompt

            result["score"] = 1.0
            return result

        return result

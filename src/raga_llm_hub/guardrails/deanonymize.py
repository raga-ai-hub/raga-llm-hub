import re
from enum import Enum
from typing import Dict, List, Tuple, Union

import fuzzysearch

from .vault import Vault


class MatchingStrategy(Enum):
    """
    An enum for the different matching strategies used to find placeholders in the model output.
    """

    EXACT = "exact"
    CASE_INSENSITIVE = "case_insensitive"
    FUZZY = "fuzzy"
    COMBINED_EXACT_FUZZY = "combined_exact_fuzzy"

    @staticmethod
    def _match_exact(text: str, vault_items: List[Tuple]) -> str:
        """
        Replaces placeholders in the model output with real values from the vault.

        Parameters:
            text (str): The model output.
            vault_items (List[Tuple]): The list of items in the vault.
        """
        for vault_item in vault_items:
            text = text.replace(vault_item[0], vault_item[1])

        return text

    @staticmethod
    def _match_case_insensitive(text: str, vault_items: List[Tuple]) -> str:
        """
        It replaces all the anonymized entities with the original ones
        irrespective of their letter case.

        Examples of matching:
            keanu reeves -> Keanu Reeves
            JOHN F. KENNEDY -> John F. Kennedy

        Parameters:
            text (str): The model output.
            vault_items (List[Tuple]): The list of items in the vault.
        """
        for vault_item in vault_items:
            text = re.sub(vault_item[0], vault_item[1], text, flags=re.IGNORECASE)

        return text

    @staticmethod
    def _match_fuzzy(text: str, vault_items: List[Tuple], max_l_dist: int = 3) -> str:
        """
        It uses fuzzy matching to find the position of the anonymized entity in the text.
        It replaces all the anonymized entities with the original ones.

        Examples of matching:
            Kaenu Reves -> Keanu Reeves
            John F. Kennedy -> John Kennedy

        Parameters:
            text (str): The model output.
            vault_items (List[Tuple]): The list of items in the vault.
        """

        for vault_item in vault_items:
            matches = fuzzysearch.find_near_matches(
                vault_item[0], text, max_l_dist=max_l_dist
            )

            new_text = ""
            last_end = 0
            for m in matches:
                # add the text that isn't part of a match
                new_text += text[last_end : m.start]
                # add the replacement text
                new_text += vault_item[1]
                last_end = m.end
            # add the remaining text that wasn't part of a match
            new_text += text[last_end:]
            text = new_text

        return text

    def match(self, text: str, vault_items: List[Tuple]) -> str:
        if self == MatchingStrategy.EXACT:
            return self._match_exact(text, vault_items)

        if self == MatchingStrategy.CASE_INSENSITIVE:
            return self._match_case_insensitive(text, vault_items)

        if self == MatchingStrategy.FUZZY:
            return self._match_fuzzy(text, vault_items)

        if self == MatchingStrategy.COMBINED_EXACT_FUZZY:
            text = self._match_exact(text, vault_items)
            text = self._match_fuzzy(text, vault_items)
            return text

        return text


class Deanonymize:
    """
    A class for replacing placeholders in the model output with real values from a vault.

    This class uses the Vault class to access stored values and replaces any placeholders
    in the model's output with their corresponding values from the vault.
    """

    def __init__(
        self,
        prompt: str,
        vault: Vault,
        matching_strategy: Union[MatchingStrategy, str] = MatchingStrategy.EXACT,
    ):
        """
        Initializes an instance of the Deanonymize class.

        Parameters:
            vault (Vault): An instance of the Vault class which stores the real values.
            matching_strategy (str): The strategy used to find placeholders in the model output. Value can be "exact", "case_insensitive","fuzzy","combined_exact_fuzzy". Defaults to the "exact" matching.
        """

        self._prompt = prompt
        if isinstance(matching_strategy, str):
            matching_strategy = MatchingStrategy(matching_strategy)

        self._vault = vault
        self._matching_strategy = matching_strategy

    def run(self):
        result: Dict[str, Union[str, bool, float]] = {
            "prompt": self._prompt,
            "is_passed": False,
            "score": 1.0,
            "evaluated_with": {"matching_strategy": self._matching_strategy.value},
        }
        vault_items = self._vault.get()
        if not vault_items:
            result["reason"] = (
                "No values found to replace, need to run Anonymize Guardrail first."
            )
            result["is_passed"] = False
            result["score"] = 0.0
            return result
        output = self._matching_strategy.match(self._prompt, vault_items)

        result["sanitized_prompt"] = output
        result["is_passed"] = True
        result["score"] = 0.0
        return result

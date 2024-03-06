import json
import os
from typing import Dict, List, Optional, Sequence

from presidio_anonymizer import AnonymizerEngine

from .anonymize import Anonymize
from .anonymize_helpers import get_analyzer, get_transformers_recognizer

BERT_BASE_NER_CONF = {
    "PRESIDIO_SUPPORTED_ENTITIES": [
        "LOCATION",
        "PERSON",
        "ORGANIZATION",
    ],
    "DEFAULT_MODEL_PATH": "dslim/bert-base-NER",
    "ONNX_MODEL_PATH": "dslim/bert-base-NER",
    "LABELS_TO_IGNORE": ["O", "CARDINAL"],
    "DEFAULT_EXPLANATION": "Identified as {} by the dslim/bert-base-NER NER model",
    "SUB_WORD_AGGREGATION": "simple",
    "DATASET_TO_PRESIDIO_MAPPING": {
        "MISC": "O",
        "LOC": "LOCATION",
        "ORG": "ORGANIZATION",
        "PER": "PERSON",
    },
    "MODEL_TO_PRESIDIO_MAPPING": {
        "MISC": "O",
        "LOC": "LOCATION",
        "ORG": "ORGANIZATION",
        "PER": "PERSON",
    },
    "CHUNK_OVERLAP_SIZE": 40,
    "CHUNK_SIZE": 600,
    "ID_SCORE_MULTIPLIER": 0.4,
    "ID_ENTITY_NAME": "ID",
}

default_entity_types = [
    "CREDIT_CARD",
    "CRYPTO",
    "EMAIL_ADDRESS",
    "IBAN_CODE",
    "IP_ADDRESS",
    "PERSON",
    "PHONE_NUMBER",
    "US_SSN",
    "US_BANK_NUMBER",
    "CREDIT_CARD_RE",
    "UUID",
    "EMAIL_ADDRESS_RE",
    "US_SSN_RE",
]

sensitive_patterns_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "resources",
    "sensitive_patterns.json",
)


class Sensitive:
    """
    A class used to detect sensitive (PII) data in the output of a language model.

    This class uses the Presidio Analyzer Engine and predefined internally patterns (sensitive_patterns.json) to analyze the output for specified entity types.
    If no entity types are specified, it defaults to checking for all entity types.
    """

    def __init__(
        self,
        prompt,
        response,
        threshold=0.5,
        entity_types: Optional[Sequence[str]] = None,
        regex_pattern_groups_path: str = sensitive_patterns_path,
        redact: bool = True,
        recognizer_conf: Optional[Dict] = BERT_BASE_NER_CONF,
        use_onnx: bool = False,
    ):
        """
        Initializes an instance of the Sensitive class.

        Args:
        - question: str, the question to be evaluated for contextual relevancy
        - response: str, the response for the question
        - entity_types (Optional[Sequence[str]]): The entity types to look for in the output. Defaults to all
                                               entity types.
        - regex_pattern_groups_path (str): Path to the regex patterns file. Default is sensitive_patterns.json.
        - redact (bool): Redact found sensitive entities. Default to False.
        - recognizer_conf (Optional[Dict]): Configuration to recognize PII data. Default is dslim/bert-base-NER.
        - threshold (float): Acceptance threshold. Default is 0.
        - use_onnx (bool): Use ONNX model for inference. Default is False.
        """
        self._prompt = prompt
        self._output = response
        self._threshold = threshold

        if not entity_types:
            entity_types = default_entity_types.copy()
        entity_types.append("CUSTOM")

        self._entity_types = entity_types
        self._redact = redact
        self._threshold = threshold

        transformers_recognizer = get_transformers_recognizer(recognizer_conf, use_onnx)
        self._analyzer = get_analyzer(
            transformers_recognizer,
            self._get_regex_patterns(regex_pattern_groups_path),
            [],
        )
        self._anonymizer = AnonymizerEngine()

    @staticmethod
    def _get_regex_patterns(json_path: str) -> List[dict]:  # type: ignore
        """
        Load regex patterns from a specified JSON file.

        Parameters:
            json_path (str): Path to the JSON file containing regex patterns.

        Returns:
            List[dict]: List of regex patterns with each dictionary containing "name", "expressions", "context", and "score".
                        Returns an empty list if file not found or parsing error occurred.
        """
        regex_groups = []
        with open(json_path, "r") as myfile:
            pattern_groups_raw = json.load(myfile)
        for group in pattern_groups_raw:
            regex_groups.append(
                {
                    "name": group["name"].upper(),
                    "expressions": group.get("expressions", []),
                    "context": group.get("context", []),
                    "score": group.get("score", 0.75),
                    "languages": group.get("languages", ["en"]),
                    "reuse": group.get("reuse", False),
                }
            )
        return regex_groups

    def run(self):
        result = {
            "prompt": self._prompt,
            "response": self._output,
            "threshold": self._threshold,
            "evaluated_with": {
                "threshold": self._threshold,
                "redact": self._redact,
            },
        }

        if self._prompt.strip() == "":
            result["sanitized_response"] = self._output
            result["score"] = 1.0
            result["is_passed"] = True

            return result

        analyzer_results = self._analyzer.analyze(
            text=Anonymize.remove_single_quotes(self._output),
            language="en",
            entities=self._entity_types,
            score_threshold=self._threshold,
        )

        if analyzer_results:
            if self._redact:
                result["reason"] = "Redacting sensitive entities"
                anonymize_result = self._anonymizer.anonymize(
                    text=self._output, analyzer_results=analyzer_results
                )

                result["sanitized_response"] = anonymize_result.text

            risk_score = max(
                analyzer_result.score for analyzer_result in analyzer_results
            )

            result["reason"] = "Sensitive data found in the output"
            result["score"] = 1 - risk_score
            result["is_passed"] = "Failed" if (risk_score) > self._threshold else True

            return result

        result["reason"] = "No sensitive data found in the output"
        result["sanitized_response"] = self._output
        result["score"] = 1.0
        result["is_passed"] = True

        return result

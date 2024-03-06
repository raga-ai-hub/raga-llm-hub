from typing import Dict, Optional

from .utils import pipeline

model_path = "papluca/xlm-roberta-base-language-detection"


class LanguageSame:
    """
    LanguageSame class is responsible for detecting and comparing the language of given prompt and model output to ensure they are the same.
    """

    def __init__(
        self,
        prompt,
        response,
        threshold=0.1,
        transformers_kwargs: Optional[Dict] = None,
    ):
        """
        Initializes the LanguageSame scanner.

        Args:
        - question: str, the question to be evaluated for contextual relevancy
        - retrieval_context: list of str, the retrieval context for the question
        - include_reason: bool, whether to include the reason for the evaluation (default True)
        - model: str, the name of the OpenAI model to be used (default 'gpt-3.5-turbo')
        - threshold: float, the threshold for the relevancy score (default 0.5)
        - use_onnx (bool): Whether to use ONNX for inference. Default is False.
        - transformers_kwargs (dict): Additional keyword arguments to pass to the transformers pipeline.
        """
        self.prompt = prompt
        self.output = response
        self._threshold = threshold

        transformers_kwargs = transformers_kwargs or {}
        transformers_kwargs["max_length"] = 512
        transformers_kwargs["truncation"] = True
        transformers_kwargs["top_k"] = None

        self._pipeline = pipeline(
            task="text-classification",
            model=model_path,
            **transformers_kwargs,
        )

        self.supported_languages = {
            "ar": "Arabic",
            "bg": "Bulgarian",
            "de": "German",
            "el": "Modern Greek",
            "en": "English",
            "es": "Spanish",
            "fr": "French",
            "hi": "Hindi",
            "it": "Italian",
            "ja": "Japanese",
            "nl": "Dutch",
            "pl": "Polish",
            "pt": "Portuguese",
            "ru": "Russian",
            "sw": "Swahili",
            "th": "Thai",
            "tr": "Turkish",
            "ur": "Urdu",
            "vi": "Vietnamese",
            "zh": "Chinese",
        }

    def run(self):
        detected_languages = self._pipeline([self.prompt, self.output])
        prompt_language = max(detected_languages[0], key=lambda x: x["score"])["label"]
        response_language = max(detected_languages[1], key=lambda x: x["score"])[
            "label"
        ]

        # get the score of the prompt language in detected languages[1]
        for language in detected_languages[1]:
            if language["label"] == prompt_language:
                response_score = language["score"]

        reason = f"Detected {self.supported_languages[prompt_language]} in prompt & {self.supported_languages[response_language]} in response!"

        result = {
            "prompt": self.prompt,
            "response": self.output,
            "score": response_score,
            "threshold": self._threshold,
            "is_passed": True if response_score >= self._threshold else False,
            "reason": reason,
        }

        return result

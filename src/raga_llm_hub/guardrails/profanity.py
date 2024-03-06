from typing import Dict, Optional

from .utils import pipeline

_model_path = ("IMSyPP/hate_speech_en",)

_profanity_labels = [
    "LABEL_1",
    "LABEL_2",
    "LABEL_3",
]


class Profanity:
    """
    This scanner is used to scan and detect Profanity in the response.
    """

    def __init__(
        self,
        question,
        response,
        threshold=0.5,
        use_onnx: bool = False,
        transformers_kwargs: Optional[Dict] = None,
    ):
        """
        Initializes an instance of the Profanity class.

        Args:
        - question: str, the question to be evaluated for profanity check
        - response: str, the response for the question
        - threshold: float, the threshold for the malicious score (default 0.5)
        - use_onnx (bool): Whether to use the ONNX version of the model. Defaults to False.
        - transformers_kwargs (dict): Additional keyword arguments to pass to the transformers pipeline.
        """
        self.prompt = question
        self.output = response
        self._threshold = threshold

        transformers_kwargs = transformers_kwargs or {}
        transformers_kwargs["max_length"] = 512
        transformers_kwargs["truncation"] = True
        transformers_kwargs["top_k"] = None

        self._classifier = pipeline(
            task="text-classification",
            model=_model_path[0],
            use_onnx=use_onnx,
            **transformers_kwargs,
        )

    def getans(self, input_data):
        profanity_score = 0
        for item in input_data[0]:
            if item["label"] in _profanity_labels:
                profanity_score += item["score"]

        return profanity_score

    def run(self):
        results = self._classifier(self.output)
        score = self.getans(results)

        result = {
            "prompt": self.prompt,
            "response": self.output,
            "score": score,
            "threshold": self._threshold,
            "is_passed": True if score > self._threshold else False,
        }
        return result

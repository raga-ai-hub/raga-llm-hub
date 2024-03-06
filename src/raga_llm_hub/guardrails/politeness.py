from typing import Dict, Optional

from .utils import pipeline

model_path = ("Genius1237/xlm-roberta-large-tydip",)


class Politeness:
    """
    Used to test whether model response is polite or not.
    """

    def __init__(
        self,
        prompt,
        threshold=0.5,
    ):
        """
        Initializes the Politeness class.

        Args:
        - prompt: str, the text to be evaluated for Politeness.
        - threshold: float, the threshold for the Politeness test (default 0.5)
        """
        self.prompt = prompt
        self._threshold = threshold

        self._pipeline = pipeline(
            task="text-classification",
            model=model_path[0],
        )

    def run(self):
        score_p = 0
        response = self._pipeline(self.prompt)
        if len(response) == 1:
            response = response[0]
        if response["label"] == "polite":
            score_p = 0
        else:
            score_p = response["score"]
        print(response, "r")
        result = {
            "prompt": self.prompt,
            "score": score_p,
            "threshold": self._threshold,
            "is_passed": False if score_p >= self._threshold else True,
            "evaluated_with": {"task": self._pipeline.task},
        }

        return result

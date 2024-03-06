from typing import Dict, Optional

from .utils import pipeline

model_path = ("michellejieli/NSFW_text_classifier",)


class NSFW:
    """
    Not safe for work class is responsible for detecting language which is not suitable for work place, specifically text that is considered inappropriate and unprofessional.
    """

    def __init__(
        self,
        prompt,
        threshold=0.5,
    ):
        """
        Initializes the NSFW class.

        Args:
        - prompt: str, the text to be evaluated for nsfw.
        - threshold: float, the threshold for the nsfw test (default 0.5)
        """
        self.prompt = prompt
        self._threshold = threshold

        self._pipeline = pipeline(
            task="sentiment-analysis",
            model=model_path[0],
        )

    def run(self):
        score_nsfw = 0
        response = self._pipeline(self.prompt)
        if len(response) == 1:
            response = response[0]
        if response["label"] == "SFW":
            score_nsfw = 0
        else:
            score_nsfw = response["score"]
        print(response, "r")
        result = {
            "prompt": self.prompt,
            "score": score_nsfw,
            "threshold": self._threshold,
            "is_passed": False if score_nsfw >= self._threshold else True,
            "evaluated_with": {"task": self._pipeline.task},
        }

        return result

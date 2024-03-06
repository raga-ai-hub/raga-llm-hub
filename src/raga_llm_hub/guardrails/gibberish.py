from .utils import pipeline

model_path = ("madhurjindal/autonlp-Gibberish-Detector-492513457",)


class Gibberish:
    """
    Main aim of this class is to classify user input as either gibberish or non-gibberish, enabling more accurate and meaningful interactions with the system.
    """

    def __init__(
        self,
        prompt,
        threshold=0.5,
    ):
        """
        Initializes the Gibberish class.

        Args:
        - prompt: str, the text to be evaluated for nsfw.
        - threshold: float, the threshold for the nsfw test (default 0.5)
        """
        self.prompt = prompt
        self._threshold = threshold

        self._pipeline = pipeline(
            task="text-classification",
            model=model_path[0],
        )

    def run(self):
        gibberish_score = 0
        response = self._pipeline(self.prompt)
        if len(response) == 1:
            response = response[0]
        if response["label"] == "clean":
            gibberish_score = 0
        else:
            gibberish_score = response["score"]
        print(response, "res")
        result = {
            "prompt": self.prompt,
            "score": gibberish_score,
            "threshold": self._threshold,
            "is_passed": False if gibberish_score >= self._threshold else True,
            "evaluated_with": {"task": self._pipeline.task},
        }

        return result

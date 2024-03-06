from typing import Dict, Optional, Union

from .match_type import MatchType

from .anonymize_helpers.transformers_helpers import pipeline


_model = {
    "path": "ProtectAI/distilroberta-base-rejection-v1",
    "onnx_path": "ProtectAI/distilroberta-base-rejection-v1",
    "max_length": 512,
}


class NoRefusal:
    """
    A class used to detect and handle refusals in language model output.

    Refusals are common when the prompt breaches policies defined by the model.
    """

    def __init__(
        self,
        question,
        response,
        threshold=0.75,
        match_type: Union[MatchType, str] = MatchType.FULL,
        use_onnx: bool = False,
        transformers_kwargs: Optional[Dict] = None,
    ):
        """
        Initializes an instance of the NoRefusal class.

        Args:
        - question: str, the question to be evaluated for contextual relevancy
        - retrieval_context: list of str, the retrieval context for the question
        - include_reason: bool, whether to include the reason for the evaluation (default True)
        - model: str, the name of the OpenAI model to be used (default 'gpt-3.5-turbo')
        - threshold: float, the threshold for the relevancy score (default 0.5)
        - temperature: int, the temperature for model completion (default 0)

        threshold (float): The similarity threshold to consider an output as refusal.
            match_type (str): Whether to match the "full" text or individual "sentences". Default is "full".
            use_onnx (bool): Whether to use the ONNX version of the model. Defaults to False.
            transformers_kwargs (dict): Additional keyword arguments to pass to the transformers pipeline.
        """
        self.question = question
        self.output = response
        self._threshold = threshold

        if isinstance(match_type, str):
            match_type = MatchType(match_type)

        self._match_type = match_type

        transformers_kwargs = transformers_kwargs or {}
        transformers_kwargs["max_length"] = _model["max_length"]
        transformers_kwargs["truncation"] = True

        self._pipeline = pipeline(
            task="text-classification",
            model=_model["path"],
            onnx_model=_model["onnx_path"],
            use_onnx=use_onnx,
            **transformers_kwargs,
        )

    def run(self):
        result = {
            "prompt": self.question,
            "response": self.output,
            "threshold": self._threshold,
        }

        if self.output.strip() == "":
            result["score"] = 1.0
            result["is_passed"] = True
            return result

        results_all = self._pipeline(self._match_type.get_inputs(self.output))
        highest_score = 0.0

        for result in results_all:
            score = round(
                (
                    1 - result["score"]
                    if result["label"] == "REJECTION"
                    else result["score"]
                ),
                2,
            )

            if score > highest_score:
                highest_score = score

        result = {
            "prompt": self.question,
            "response": self.output,
            "score": highest_score,
            "threshold": self._threshold,
            "is_passed": True if highest_score < self._threshold else False,
        }

        return result

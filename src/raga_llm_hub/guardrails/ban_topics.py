import warnings
from typing import Any, Dict, Optional, Sequence

from .anonymize_helpers.transformers_helpers import pipeline

# This model was trained on a mixture of 33 datasets and 389 classes reformatted in the universal NLI format.
# The model is English only. You can also use it for multilingual zeroshot classification by first machine translating texts to English.
MODEL_LARGE = {
    "path": "MoritzLaurer/deberta-v3-large-zeroshot-v1.1-all-33",
    "onnx_path": "MoritzLaurer/deberta-v3-large-zeroshot-v1.1-all-33",
    "max_length": 512,
}
# This is essentially the same as its larger sister MoritzLaurer/deberta-v3-large-zeroshot-v1.1-all-33 only that it's smaller.
# Use it if you need more speed. The model is English-only.
MODEL_BASE = {
    "path": "MoritzLaurer/deberta-v3-base-zeroshot-v1.1-all-33",
    "onnx_path": "MoritzLaurer/deberta-v3-base-zeroshot-v1.1-all-33",
    "max_length": 512,
}
# Same as above, just smaller/faster.
MODEL_XSMALL = {
    "path": "MoritzLaurer/deberta-v3-xsmall-zeroshot-v1.1-all-33",
    "onnx_path": "MoritzLaurer/deberta-v3-xsmall-zeroshot-v1.1-all-33",
    "max_length": 512,
}
# Same as above, just even faster. The model only has 22 million backbone parameters.
# The model is 25 MB small (or 13 MB with ONNX quantization).
MODEL_XTREMEDISTIL = {
    "path": "MoritzLaurer/xtremedistil-l6-h256-zeroshot-v1.1-all-33",
    "onnx_path": "MoritzLaurer/xtremedistil-l6-h256-zeroshot-v1.1-all-33",
    "max_length": 512,
}

ALL_MODELS = [MODEL_LARGE, MODEL_BASE, MODEL_XSMALL, MODEL_XTREMEDISTIL]


class BanTopics:
    """
    BanTopics class is used to ban certain topics from the prompt.

    It uses a HuggingFace model to perform zero-shot classification.
    """

    def __init__(
        self,
        prompt: str,
        topics: Sequence[str],
        threshold: float = 0.6,
        model: Optional[Dict] = None,
        use_onnx: bool = False,
        transformers_kwargs: Optional[Dict] = None,
    ):
        """
        Initialize BanTopics object.

        Parameters:
            prompt (str): Prompt to check for banned topics.
            topics (Sequence[str]): List of topics to ban.
            threshold (float, optional): Threshold to determine if a topic is present in the prompt. Default is 0.75.
            model (Dict, optional): Model to use for zero-shot classification. Default is deberta-v3-base-zeroshot-v1.
            use_onnx (bool, optional): Whether to use ONNX for inference. Default is False.
            transformers_kwargs (Dict, optional): Additional kwargs to pass to the transformers pipeline. Default is None.

        Raises:
            ValueError: If no topics are provided.
        """
        self._model = model
        if model is None:
            model = MODEL_BASE

        if model not in ALL_MODELS:
            warnings.warn(
                f"Model must be in the list of allowed: {ALL_MODELS}, switching to default model"
            )
            model = MODEL_BASE

        self._prompt = prompt
        self._topics = topics
        self._threshold = threshold

        transformers_kwargs = transformers_kwargs or {}
        transformers_kwargs["max_length"] = model["max_length"]
        transformers_kwargs["truncation"] = True

        self._classifier = pipeline(
            task="zero-shot-classification",
            model=model["path"],
            onnx_model=model["onnx_path"],
            use_onnx=use_onnx,
            **transformers_kwargs,
        )

    def run(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "prompt": self._prompt,
            "reason": "No banned topics found in prompt.",
            "is_passed": True,
            "score": 0.0,
            "evaluated_with": {"topics": self._topics, "model": self._model},
        }
        prompt = self._prompt

        if self._prompt.strip() == "":
            return result

        output_model = self._classifier(prompt, self._topics, multi_label=False)

        max_score = round(
            max(output_model["scores"]) if output_model["scores"] else 0, 2
        )
        result["score"] = max_score

        if max_score > self._threshold:
            result["reason"] = "Banned topics found in prompt."
            result["is_passed"] = False
            result["score"] = dict(zip(output_model["labels"], output_model["scores"]))

        return result

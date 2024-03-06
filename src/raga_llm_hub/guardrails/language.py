from enum import Enum
from typing import Dict, List, Literal, Optional, Sequence, Union, get_args

import transformers
from transformers import (PreTrainedModel, PreTrainedTokenizer,
                          PreTrainedTokenizerFast, TFPreTrainedModel)

from .anonymize_helpers.transformers_helpers import (
    _ort_model_for_sequence_classification, device, get_tokenizer,
    is_onnx_supported)
from .utils import calculate_risk_score, split_text_by_sentences

ClassificationTask = Literal["text-classification", "zero-shot-classification"]


def pipeline(
    task: str,
    model: Union[PreTrainedModel, TFPreTrainedModel],
    tokenizer: Union[PreTrainedTokenizer, PreTrainedTokenizerFast],
    **kwargs,
):
    if task not in get_args(ClassificationTask):
        raise ValueError(f"Invalid task. Must be one of {ClassificationTask}")

    return transformers.pipeline(
        task,
        model=model,
        tokenizer=tokenizer,
        device=device(),
        batch_size=1,
        **kwargs,
    )


def get_tokenizer_and_model_for_classification(
    model: str, onnx_model: Optional[str] = None, use_onnx: bool = False, **kwargs
):
    """
    This function loads a tokenizer and model given a model identifier and caches them.
    Subsequent calls with the same model_identifier will return the cached tokenizer.

    Args:
        model (str): The model identifier to load the tokenizer and model for.
        onnx_model (Optional[str]): The model identifier to load the ONNX model for. Defaults to None.
        use_onnx (bool): Whether to use the ONNX version of the model. Defaults to False.
        **kwargs: Keyword arguments to pass to the tokenizer and model.
    """
    tf_tokenizer = get_tokenizer(model, **kwargs)

    if kwargs.get("max_length", None) is None:
        kwargs["max_length"] = tf_tokenizer.model_max_length

    if use_onnx and is_onnx_supported() is False:
        use_onnx = False

    if use_onnx is False:
        tf_model = transformers.AutoModelForSequenceClassification.from_pretrained(
            model, **kwargs
        )

        return tf_tokenizer, tf_model

    subfolder = "onnx" if onnx_model == model else ""
    if onnx_model is not None:
        model = onnx_model

    # Hack for some models
    tf_tokenizer.model_input_names = ["input_ids", "attention_mask"]

    tf_model = _ort_model_for_sequence_classification(
        model, export=onnx_model is None, subfolder=subfolder, **kwargs
    )

    return tf_tokenizer, tf_model


default_model_path = (
    "papluca/xlm-roberta-base-language-detection",
    "ProtectAI/xlm-roberta-base-language-detection-onnx",
)


class MatchType(Enum):
    SENTENCE = "sentence"
    FULL = "full"

    def get_inputs(self, prompt: str) -> List[str]:
        if self == MatchType.SENTENCE:
            return split_text_by_sentences(prompt)

        return [prompt]


class Language:
    """
    A Scanner subclass responsible for determining the language of a given text
    prompt and verifying its validity against a list of predefined languages.

    Note: when no languages are detected above the threshold, the prompt is considered valid.
    """

    def __init__(
        self,
        prompt: str,
        valid_languages: Sequence[str],
        model_path: Optional[str] = None,
        threshold: float = 0.6,
        match_type: Union[MatchType, str] = MatchType.FULL,
        use_onnx: bool = False,
        model_kwargs: Optional[Dict] = None,
        pipeline_kwargs: Optional[Dict] = None,
    ):
        """
        Initializes the Language scanner with a list of valid languages.

        Parameters:
            prompt (str): The prompt to check for language.
            valid_languages (Sequence[str]): A list of valid language codes in ISO 639-1.
            threshold (float): Minimum confidence score.
            match_type (MatchType): Whether to match the full text or individual sentences. Default is MatchType.FULL.
            use_onnx (bool): Whether to use ONNX for inference. Default is False.
            model_kwargs (Dict): Keyword arguments passed to the model.
            pipeline_kwargs (Dict): Keyword arguments passed to the pipeline.
        """
        if isinstance(match_type, str):
            match_type = MatchType(match_type)

        self._prompt = prompt
        self._threshold = threshold
        self._valid_languages = valid_languages
        self._match_type = match_type

        default_pipeline_kwargs = {
            "max_length": 512,
            "truncation": True,
            "top_k": None,
        }
        if pipeline_kwargs is None:
            pipeline_kwargs = {}

        pipeline_kwargs = {**default_pipeline_kwargs, **pipeline_kwargs}
        model_kwargs = model_kwargs or {}

        onnx_model_path = model_path
        if model_path is None:
            model_path = default_model_path[0]
            onnx_model_path = default_model_path[1]

        tf_tokenizer, tf_model = get_tokenizer_and_model_for_classification(
            model=model_path,
            onnx_model=onnx_model_path,
            use_onnx=use_onnx,
            **model_kwargs,
        )

        # print("tf_model", tf_model)

        self._pipeline = pipeline(
            task="text-classification",
            model=tf_model,
            tokenizer=tf_tokenizer,
            **pipeline_kwargs,
        )

    def run(self):
        result = {
            "prompt": self._prompt,
            "is_passed": True,
            "score": 0.0,
            "evaluated_with": {
                "match_type": self._match_type.value,
                "valid_languages": self._valid_languages,
                "threshold": self._threshold,
            },
            "reason": "",
        }
        prompt = self._prompt
        if prompt.strip() == "":
            return result

        results_all = self._pipeline(self._match_type.get_inputs(prompt))
        for result_chunk in results_all:
            languages_above_threshold = [
                result["label"]
                for result in result_chunk
                if result["score"] > self._threshold
            ]

            highest_score = max([result["score"] for result in result_chunk])

            # Check if any of the languages above threshold are not valid
            if len(set(languages_above_threshold) - set(self._valid_languages)) > 0:
                result["is_passed"] = False
                result["score"] = calculate_risk_score(highest_score, self._threshold)
                result["reason"] = (
                    f"Invalid languages {languages_above_threshold} are found in the text."
                )
                return result

        result["reason"] = "Only valid languages are found in the text."

        return result

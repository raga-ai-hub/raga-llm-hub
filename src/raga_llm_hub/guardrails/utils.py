import re
from typing import List, Literal, Optional, get_args

import nltk
import structlog
import torch
import transformers
from optimum import onnxruntime as optimum_onnxruntime

LOGGER = structlog.get_logger(__name__)

url_pattern = re.compile(
    "(?:https?://(?:www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|www\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
    re.DOTALL,
)

ClassificationTask = Literal[
    "text-classification", "zero-shot-classification", "ner", "sentiment-analysis"
]


def calculate_risk_score(score: float, threshold: float) -> float:
    if score > threshold:
        return 1.0

    risk_score = round(abs(score - threshold) / threshold, 1)
    # Ensure risk score is between 0 and 1
    return min(max(risk_score, 0), 1)


def extract_urls(input_string: str) -> List[str]:
    # Regular expression pattern to match various types of strings
    pattern = r"(https?://)?(www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,})(/[^\s]*)?"
    # Find all matches in the input string
    matches = re.findall(pattern, input_string)
    # Extract strings from the matched groups
    extracted_strings = ["".join(match) for match in matches]
    return extracted_strings


def split_text_by_sentences(text: str) -> List[str]:

    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        nltk.download("punkt")

    return nltk.sent_tokenize(text.strip())


def device():
    if torch.cuda.is_available():
        return torch.device("cuda:0")
    elif torch.backends.mps.is_available():
        return torch.device("mps")

    return torch.device("cpu")


def _ort_model_for_sequence_classification(
    model: str, export: bool = False, subfolder: str = ""
):
    if device().type == "cuda":
        tf_model = (
            optimum_onnxruntime.ORTModelForSequenceClassification.from_pretrained(
                model,
                export=export,
                subfolder=subfolder,
                file_name="model.onnx",
                provider="CUDAExecutionProvider",
                use_io_binding=True,
            )
        )

        LOGGER.debug(
            "Initialized classification ONNX model", model=model, device=device()
        )

        return tf_model

    tf_model = optimum_onnxruntime.ORTModelForSequenceClassification.from_pretrained(
        model,
        export=export,
        subfolder=subfolder,
        file_name="model.onnx",
    )
    LOGGER.debug("Initialized classification ONNX model", model=model, device=device())

    return tf_model


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
    tf_tokenizer = transformers.AutoTokenizer.from_pretrained(model)

    if kwargs.get("max_length", None) is None:
        kwargs["max_length"] = tf_tokenizer.model_max_length

    if use_onnx is False:
        LOGGER.warning(
            "ONNX is not supported on this machine. Using PyTorch instead of ONNX."
        )
        use_onnx = False

    if use_onnx is False:
        tf_model = transformers.AutoModelForSequenceClassification.from_pretrained(
            model
        )
        LOGGER.debug("Initialized classification model", model=model, device=device())

        return tf_tokenizer, tf_model

    subfolder = "onnx" if onnx_model == model else ""
    if onnx_model is not None:
        model = onnx_model

    # Hack for some models
    tf_tokenizer.model_input_names = ["input_ids", "attention_mask"]

    tf_model = _ort_model_for_sequence_classification(
        model, export=onnx_model is None, subfolder=subfolder
    )

    return tf_tokenizer, tf_model


def _pipeline_ner(
    model: str, onnx_model: Optional[str] = None, use_onnx: bool = False, **kwargs
):
    tf_tokenizer = transformers.AutoTokenizer.from_pretrained(model)

    if use_onnx is False:
        LOGGER.warning(
            "ONNX is not supported on this machine. Using PyTorch instead of ONNX."
        )
        use_onnx = False

    if use_onnx:
        subfolder = "onnx" if onnx_model == model else ""
        if onnx_model is not None:
            model = onnx_model

        # optimum_onnxruntime = lazy_load_dep(
        #     "optimum.onnxruntime",
        #     "optimum[onnxruntime]" if device().type != "cuda" else "optimum[onnxruntime-gpu]",
        # )
        tf_model = optimum_onnxruntime.ORTModelForTokenClassification.from_pretrained(
            model,
            export=onnx_model is None,
            subfolder=subfolder,
            provider=(
                "CUDAExecutionProvider"
                if device().type == "cuda"
                else "CPUExecutionProvider"
            ),
            use_io_binding=True if device().type == "cuda" else False,
        )
        LOGGER.debug("Initialized NER ONNX model", model=model, device=device())
    else:
        tf_model = transformers.AutoModelForTokenClassification.from_pretrained(model)
        LOGGER.debug("Initialized NER model", model=model, device=device())

    return transformers.pipeline(
        "ner",
        model=tf_model,
        tokenizer=tf_tokenizer,
        device=device(),
        batch_size=1,
        **kwargs,
    )


def pipeline(
    task: str,
    model: str,
    onnx_model: Optional[str] = None,
    use_onnx: bool = False,
    **kwargs,
):
    if task not in get_args(ClassificationTask):
        raise ValueError(f"Invalid task. Must be one of {ClassificationTask}")

    if task == "ner":
        return _pipeline_ner(model, onnx_model, use_onnx, **kwargs)

    tf_tokenizer, tf_model = get_tokenizer_and_model_for_classification(
        model, onnx_model, use_onnx, **kwargs
    )

    return transformers.pipeline(
        task,
        model=tf_model,
        tokenizer=tf_tokenizer,
        device=device(),
        batch_size=1,
        **kwargs,
    )

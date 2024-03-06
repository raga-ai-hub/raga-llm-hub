import torch

from .utils import device, get_tokenizer_and_model_for_classification

MODEL_BASE = {
    "path": "MoritzLaurer/deberta-v3-base-zeroshot-v1.1-all-33",
    "onnx_path": "MoritzLaurer/deberta-v3-base-zeroshot-v1.1-all-33",
    "max_length": 512,
}

_model = MODEL_BASE


class FactualConsistency:
    """
    FactualConsistency Class:

    This class checks for entailment between a given prompt and output using a pretrained NLI model.
    """

    def __init__(self, prompt, response, threshold=0.5, use_onnx=False):
        """
        Initializes an instance of the Refutation class.

        Args:
        - question: str, the question to be evaluated for contextual relevancy
        - retrieval_context: list of str, the retrieval context for the question
        - include_reason: bool, whether to include the reason for the evaluation (default True)
        - model: str, the name of the OpenAI model to be used (default 'gpt-3.5-turbo')
        - threshold: float, The minimum entailment score for the output to be considered valid (default 0.5)
        - temperature: int, the temperature for model completion (default 0)
        - use_onnx (bool): Whether to use the ONNX version of the model. Defaults to False.
        """
        self.prompt = prompt
        self.output = response
        self._minimum_score = threshold

        self._tokenizer, self._model = get_tokenizer_and_model_for_classification(
            model=_model["path"],
            onnx_model=_model["onnx_path"],
            use_onnx=use_onnx,
        )
        self._model = self._model.to(device())

    def run(self):
        score = 0.0

        if self.prompt.strip() == "":
            score = 1.0

        tokenized_input_seq_pair = self._tokenizer(
            self.output, self.prompt, padding=True, truncation=True, return_tensors="pt"
        ).to(device())

        model_output = self._model(
            tokenized_input_seq_pair["input_ids"],
            tokenized_input_seq_pair["attention_mask"],
        )
        model_prediction = torch.softmax(model_output["logits"][0], -1).tolist()

        label_names = ["entailment", "not_entailment"]
        prediction = {
            name: round(float(pred), 2)
            for pred, name in zip(model_prediction, label_names)
        }

        score = prediction["entailment"]

        result = {
            "prompt": self.prompt,
            "response": self.output,
            "score": score,
            "threshold": self._minimum_score,
            "is_passed": True if score >= self._minimum_score else False,
            "evaluated_with": {"model": _model["path"]},
        }

        return result

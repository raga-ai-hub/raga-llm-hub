from typing import List, Optional

import tiktoken


class TokenLimit:
    def __init__(
        self, question, encoding_name="cl100k_base", model=None, threshold=4096
    ):
        """
        Initialize the TokenLimit object.

        Args:
        question (str): The question to be asked.
        encoding_name (str): The name of the encoding that should be used
        model (str): The name of the OpenAI model to be used for tokenization. Default is None.
        threshold (float): The threshold for the token limit. Default is 4096.
        """
        self.question = question
        self.model_name = model

        self.encoding_name = encoding_name

        if not self.model_name:
            self._encoding = tiktoken.get_encoding(self.encoding_name)
        else:
            self._encoding = tiktoken.encoding_for_model(self.model_name)

        self._limit = threshold

    def _split_text_on_tokens(self, text: str):
        """
        Splits the prompt into chunks of allowed size and tokens
        """
        splits: List[str] = []
        input_ids = self._encoding.encode(text)
        start_idx = 0
        cur_idx = min(start_idx + self._limit, len(input_ids))
        chunk_ids = input_ids[start_idx:cur_idx]

        while start_idx < len(input_ids):
            splits.append(self._encoding.decode(chunk_ids))
            start_idx += self._limit
            cur_idx = min(start_idx + self._limit, len(input_ids))
            chunk_ids = input_ids[start_idx:cur_idx]

        return splits, len(input_ids)

    def run(self):
        """
        Run the token limit test and return the result as a JSON object.
        """

        chunks, num_tokens = self._split_text_on_tokens(text=self.question)

        result = {
            "prompt": self.question,
            "is_passed": True if num_tokens < self._limit else False,
            "score": num_tokens,
            "sanitized_prompt": chunks[0],
            "evaluated_with": {
                "model": self.model_name,
                "encoding_name": self.encoding_name,
            },
        }

        return result

"""
Helper functions for tests
"""

import os
import sys
from typing import List

import spacy
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def get_nlp_model():
    """
    Function to load and cache the spaCy NLP model.
    :return: Loaded spaCy NLP model.
    """
    model_name = "en_core_web_lg"
    cache = {}

    # check if model_name is already installed else install it
    if model_name not in spacy.util.get_installed_models():
        spacy.cli.download(model_name)

    def load_model():
        if model_name not in cache:
            print(f"Loading {model_name} model...")
            cache[model_name] = spacy.load(model_name)
        return cache[model_name]

    return load_model


def analyze_words(pos_words, sentence):
    """
    This function analyzes the given words in a sentence using spaCy for lemmatization and POS matching.
    :param pos_words: list of words with their corresponding POS tags
    :param sentence: input sentence to be analyzed
    :return: a tuple containing the found lemmatized words and the found words with their POS tags
    """
    load_nlp_model = get_nlp_model()
    nlp = load_nlp_model()  # Load or retrieve the cached model
    doc = nlp(sentence)

    # Prepare the inputs
    input_dict = {word.split("_")[0]: word.split("_")[1] for word in pos_words}

    # Lemmatization and POS matching
    found_words = [tok.lemma_ for tok in doc if tok.lemma_ in input_dict.keys()]
    found_pos_words = [
        tok.lemma_ + "_" + tok.pos_
        for tok in doc
        if tok.lemma_ in input_dict.keys()
        and input_dict[tok.lemma_].lower() in tok.pos_.lower()
    ]

    # take unique items
    found_words = list(set(found_words))
    found_pos_words = list(set(found_pos_words))
    return found_words, found_pos_words


def concept_list_str(concept_set):
    """
    Generate a string representation of a list of concepts with specified replacements.
    """
    concept_strs = []
    for concept in concept_set:
        concept_strs.append(concept.replace("_N", "(noun)").replace("_V", "(verb)"))
    return ", ".join(concept_strs)


def openai_chat_request(
    client,
    model: str = "gpt-3.5-turbo",
    temperature: float = 0,
    max_tokens: int = 512,
    top_p: float = 1.0,
    frequency_penalty: float = 0,
    presence_penalty: float = 0,
    prompt: str = None,
    n: int = 1,
    messages: List[dict] = None,
    stop: List[str] = None,
    **kwargs,
) -> List[str]:
    """
    Request the evaluation prompt from the OpenAI API in chat format.
    Args:
        prompt (str): The encoded prompt.
        messages (List[dict]): The messages.
        model (str): The model to use.
        engine (str): The engine to use.
        temperature (float, optional): The temperature. Defaults to 0.7.
        max_tokens (int, optional): The maximum number of tokens. Defaults to 800.
        top_p (float, optional): The top p. Defaults to 0.95.
        frequency_penalty (float, optional): The frequency penalty. Defaults to 0.
        presence_penalty (float, optional): The presence penalty. Defaults to 0.
        stop (List[str], optional): The stop. Defaults to None.
    Returns:
        List[str]: The list of generated evaluation prompts.
    """
    assert (
        prompt is not None or messages is not None
    ), "Either prompt or messages should be provided."
    if messages is None:
        messages = [
            {
                "role": "system",
                "content": "You are an AI assistant that helps people find information.",
            },
            {"role": "user", "content": prompt},
        ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        n=n,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        stop=stop,
        **kwargs,
    )
    contents = []
    for choice in response.choices:
        # Check if the response is valid
        if choice.finish_reason not in ["stop", "length"]:
            raise ValueError(f"OpenAI Finish Reason Error: {choice.finish_reason}")
        contents.append(choice.message.content)

    return contents


def embedding_generator(texts: list):

    embeddings = model.encode(texts)
    return embeddings


class SuppressOutput:
    """
    Supress outputs
    """

    def __enter__(self):
        """
        A special method that allows the object to be used in a context manager.
        It redirects standard output and standard error to os.devnull.
        """
        # Redirect standard output and standard error to os.devnull
        # pylint: disable=attribute-defined-outside-init
        self._original_stdout = sys.stdout
        # pylint: disable=attribute-defined-outside-init
        self._original_stderr = sys.stderr
        devnull = open(os.devnull, "w", encoding="utf-8")
        sys.stdout = devnull
        sys.stderr = devnull

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Revert stdout and stderr to their original values
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr

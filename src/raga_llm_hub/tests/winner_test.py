"""
Test for comparing response with expected_response
"""

from .test_utils import concept_list_str, openai_chat_request


def winner_test(
    client,
    model_a_response,
    model_b_response,
    concept_set,
    model="gpt-3.5-turbo",
    temperature: float = 0,
    max_tokens: int = 512,
):
    cs_str = concept_list_str(concept_set)
    prompt = f"""Data : Given several concepts (i.e., nouns or verbs), we ask models to write a short and simple sentence that contains *all* the required words. The sentence should describe a common scene in daily life, and the concepts should be used in a natural way.
                Concepts: {cs_str} , Model A: {model_a_response}, Model B: {model_b_response}. Your task is to choose a better sentence from the two candidates. Decide which model's sentence is better in terms of the naturalness and commonness of the scenes they describe.
                Rules:
                - A better sentence should describe a common scene in daily life, and all concepts should be used in a natural way.
                - You should prefer sentences that use all given concepts with correct part-of-speech tags.
                - You should prefer sentences that use all given concepts with correct part-of-speech tags.
                - A simpler and shorter sentence is preferred if it describes the same scene as the other sentence.
                - If you think both sentences are equally good or bad, please choose *TIE*.
                - If you think both sentences are equally good or bad, please choose *TIE*.
                Now, please output your choice ("A" or "B" or "tie"). Your choice: """

    openai_args = {
        "client": client,
        "prompt": prompt,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "model": model,
        "stop": [],
    }

    res = openai_chat_request(**openai_args)

    res = res[0]

    if "a" in res.lower():
        output = 1.0
        reason = "The response of Model A is better"
    else:
        output = 0.0
        reason = "The response of Model B is better"

    result = {
        "model_a_response": model_a_response,
        "model_b_response": model_b_response,
        "concept_set": concept_set,
        "score": output,
        "evaluated_with": {"model": model},
        "is_passed": True,
        "reason": reason,
    }

    return result

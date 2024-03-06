import time
from functools import wraps

from openai import OpenAI

from ..tests.test_utils import embedding_generator


def raga_observer(tracer, metrics):
    def call_observer(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            print(metrics, tracer)
            t1 = time.time()
            response = function(wrapper, *args, **kwargs)
            t2 = time.time() - t1
            tokens = wrapper.response.usage.total_tokens
            result = dict()
            if "tokens" in metrics:
                result["tokens"] = tokens
            if "timetaken" in metrics:
                result["time_taken"] = (t2,)
            if "embedding" in metrics:
                result["embeding"] = embedding_generator(
                    wrapper.response.choices[0].message.content
                )
            tracer.save_run_details(tracer.observer_name, result)
            return response

        return wrapper

    return call_observer


@raga_observer("default_tracer", metrics=["tokens", "timetaken", "embedding"])
def call_openai_service(tracer_object, w, prompt):
    """
    Calls open ai service to get the response for the given prompt.

    Args:
        prompt(str): the prompt given to the model

    Returns:
        dict: A dictionary containing the prompt, response, total_tokens and timetaken for the openai response
    """
    client = tracer_object._openai_client
    messages = [{"role": "user", "content": prompt}]
    t1 = time.time()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,
        max_tokens=1000,
        top_p=0.5,
        n=1,
        frequency_penalty=0.1,
        presence_penalty=0.1,
    )
    timetaken = time.time() - t1
    w.response = response
    w.timetaken = timetaken
    contents = []
    for choice in response.choices:
        # Check if the response is valid
        if choice.finish_reason not in ["stop", "length"]:
            raise ValueError(f"OpenAI Finish Reason Error: {choice.finish_reason}")
        contents.append(choice.message.content)
    return_response = {
        "prompt": prompt,
        "timetaken": w.timetaken,
        "response": contents[0],
        "tokens_used": response.usage.total_tokens,
        "embeding": embedding_generator(response.choices[0].message.content),
    }
    return return_response

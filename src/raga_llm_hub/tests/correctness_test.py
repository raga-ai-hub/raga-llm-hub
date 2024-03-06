"""
Answer Correctness Test
"""

import json

from .template import CorrectnessTemplate


class CorrectnessTest:
    """
    This metric checks the correctness of your LLM response

    Args:
    prompt (str): The prompt for the response.
    response (str): The actual response to be evaluated.
    expected_response (str): The expected response for comparison.
    context (str): The ground truth for comparison.
    model (str): The model to be used for evaluation (default is "gpt-3.5-turbo").
    threshold (float): The threshold for correctness score (default is 0.5).

    Returns:
    dict: Result of the evaluation including correctness score, and other relevant information.
    """

    def __init__(
        self,
        client,
        prompt,
        response,
        expected_response,
        context,
        model,
        threshold,
    ):
        self.prompt = prompt
        self.response = response
        self.expected_response = expected_response
        self.context = context
        self.model_name = model
        self.threshold = threshold
        self.client = client

    def model(self, prompt):
        """
        A function to generate chat completions based on a prompt.

        Args:
            prompt (str): The prompt for generating chat completions.

        Returns:
            dict: The generated chat completions.
        """
        return self.client.chat.completions.create(
            model=self.model_name,
            temperature=0,
            messages=[{"role": "system", "content": prompt}],
        )

    def generate_correctness_prompt(self):
        """
        Generate a correctness prompt using the prompt, response, expected response, and context parameters.
        """
        return CorrectnessTemplate.generate_correctness_prompt(
            self.prompt, self.response, self.expected_response, self.context
        )

    def evaluate_response(self, statement):
        """
        Perform evaluation on the given statement using the model and return the result as a JSON object.
        """
        response = self.model(statement)
        return json.loads(response.choices[0].message.content)

    def _compute_correctness_score(self, res):
        tp = len(res["extracted_statements"]["TP"])
        fp = len(res["extracted_statements"]["FP"])
        fn = len(res["extracted_statements"]["FN"])
        correctness_score = tp / (tp + 0.5 * (fp + fn)) if tp > 0 else 0
        is_correct = True if correctness_score > self.threshold else False
        return correctness_score, is_correct

    def run(self):
        """
        Run the function to generate a correctness prompt, evaluate the response, compute correctness score, and return the result.
        """
        statement = self.generate_correctness_prompt()
        res = self.evaluate_response(statement)
        correctness_score, is_correct = self._compute_correctness_score(res)
        result = {
            "prompt": self.prompt,
            "response": self.response,
            "expected_response": self.expected_response,
            "score": correctness_score,
            "is_passed": is_correct,
            "threshold": self.threshold,
            "evaluated_with": {"model": self.model_name},
        }
        return result


# if __name__ == "__main__":
#     prompt = "What powers the sun and what is its primary function?"
#     response = "The sun is powered by nuclear fission, similar to nuclear reactors on Earth, and its primary function is to provide light to the solar system."
#     expected_response = "The sun is actually powered by nuclear fusion, not fission. In its core, hydrogen atoms fuse to form helium, releasing a tremendous amount of energy. This energy is what lights up the sun and provides heat and light, essential for life on Earth. The sun's light also plays a critical role in Earth's climate system and helps to drive the weather and ocean currents."
#     context = "The sun is actually powered by nuclear fusion, not fission. In its core, hydrogen atoms fuse to form helium, releasing a tremendous amount of energy. This energy is what lights up the sun and provides heat and light, essential for life on Earth. The sun's light also plays a critical role in Earth's climate system and helps to drive the weather and ocean currents."

#     test = AnswerCorrectnessTest(
#         prompt=prompt,
#         response=response,
#         expected_response=expected_response,
#         context=context,
#     )
#     result = test.run()
#     print(result)

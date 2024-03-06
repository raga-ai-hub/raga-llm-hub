"""
Coherence test
"""

import json

from .template import CoherenceTemplate


class CoherenceTest:
    """
    Class for testing the coherence of your LLM response

    Returns:
    dict: Result of the evaluation including coherence_test score, and other relevant information.

    """

    def __init__(
        self,
        client,
        prompt,
        response,
        context=None,
        strictness=1,
        model="gpt-4",
    ):
        """
        Initializes the test instance with the provided parameters.
        Args:
            prompt (str): The prompt for the response.
            response (str): The response to be evaluated.
            context (str): The context for the response (default is None).
            strictness (int): The number of times response is evaluated (default is 1).
            model (str): The model to be used for evaluation (default is "gpt-3.5-turbo").
        """
        self.question = prompt
        self.client = client
        self.response = response
        self.context = context
        self.model_name = model
        self.strictness = strictness
        self.strictness = (
            self.strictness if self.strictness % 2 != 0 else self.strictness + 1
        )

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

    def generate_verdict(self):
        """
        Generate a verdict using the prompt, and response.
        """
        if self.context is not None:
            question = f"{self.question} answer using context: {self.context}"
        else:
            question = self.question
        return CoherenceTemplate.generate_verdict(question, self.response)

    def evaluate(self, statement):
        """
        Evaluate the response based on the provided criteria.
        """
        response = self.model(statement)
        return json.loads(response.choices[0].message.content)

    def generate_score(self, json_response):
        """
        Extract the coherence score from the JSON response.
        """
        score = int(json_response["verdict"])
        return score

    def run(self):
        """
        Run the coherence test and return the result as a JSON object.
        """
        # Generate responses based on strictness
        responses = []
        for _ in range(self.strictness):
            verdict = self.generate_verdict()
            res = self.evaluate(verdict)
            responses.append(self.generate_score(res))

        # Compute final coherence score based on majority vote
        passed_count = sum(score != 0 for score in responses)
        coherence_score = 1 if passed_count > self.strictness / 2 else 0

        result = {
            "prompt": self.question,
            "response": self.response,
            "context": self.context,
            "is_passed": True if coherence_score != 0 else False,
            "score": coherence_score,
            "evaluated_with": {"model": self.model_name, "strictness": self.strictness},
        }

        return result

"""
Faithfulness Test
"""

import json

from .prompt_template import FaithfulnessTemplate


class FaithfulnessTest:
    def __init__(
        self,
        client,
        answer,
        retrieval_context,
        include_reason=True,
        model="gpt-3.5-turbo",
        threshold=0.5,
        temperature=0,
    ):
        """Initializes a faithfulness test instance.

        Args:
            answer (str): The text to be evaluated for faithfulness.
            retrieval_context (list): The context in which the answer is evaluated.
            include_reason (bool, optional): Whether to include the reason for the result. Defaults to True.
            model (str, optional): The model used to evaluate the answer. Defaults to "gpt-3.5-turbo".
            threshold (float, optional): The threshold for passing the faithfulness test. Defaults to 0.5.
            temperature (int, optional): The temperature. Defaults to 0.
        """
        self.retrieval_context = retrieval_context
        self.answer = answer
        self.include_reason = include_reason
        self.model_name = model
        self.threshold = threshold
        self.temperature = temperature
        self.client = client

    def model(self, prompt):
        """
        Create chat completions based on the given prompt using the specified model and temperature.

        :param prompt: The text prompt for generating chat completions.
        :return: The chat completions created by the model.
        """
        return self.client.chat.completions.create(
            model=self.model_name,
            temperature=self.temperature,
            messages=[{"role": "system", "content": prompt}],
        )

    def trim_to_json(self, response):
        """
        Trim the response content to JSON format.

        :param response: The input response object
        :type response: object

        :return: The response content in JSON format
        :rtype: dict
        """
        message_content = response.choices[0].message.content
        data = json.dumps(message_content)
        return json.loads(data)

    def generate_truths(self):
        """
        Generate truths using the retrieval context and model, and return the result.
        """
        prompt = FaithfulnessTemplate.generate_truths(self.retrieval_context)
        truths_response = self.model(prompt)
        truths = json.loads(self.trim_to_json(truths_response))
        return truths

    def generate_claims(self):
        """
        Generate claims based on the provided answer using the FaithfulnessTemplate.
        Returns the generated claims.
        """
        prompt = FaithfulnessTemplate.generate_claims(self.answer)
        claims_response = self.model(prompt)
        claims = json.loads(self.trim_to_json(claims_response))
        return claims

    def generate_verdicts(self, claims, truths):
        """
        Generate verdicts based on the given claims and truths.

        Args:
            claims: List of claims to generate verdicts for.
            truths: Retrieval context for the claims.

        Returns:
            List of verdicts generated based on the input claims and truths.
        """
        prompt = FaithfulnessTemplate.generate_verdicts(
            claims=claims, retrieval_context=truths
        )
        verdict_response = self.model(prompt)
        verdicts = json.loads(self.trim_to_json(verdict_response))["verdicts"]
        return verdicts

    def generate_score(self, verdicts):
        """
        Calculate the faithfulness score based on the given verdicts.

        Parameters:
            self (obj): The object itself.
            verdicts (list): A list of verdicts containing dictionaries with "verdict" keys.

        Returns:
            float: The faithfulness score calculated as the count of non-"no" verdicts divided by the total number of verdicts.
        """
        if len(verdicts) == 0:
            return 0

        faithfulness_count = sum(
            1 for verdict in verdicts if verdict["verdict"].strip().lower() != "no"
        )
        return faithfulness_count / len(verdicts)

    def generate_reason(self, verdicts, score):
        """
        Generate a reason based on the provided verdicts and score.

        Parameters:
            verdicts (list): A list of verdicts containing "reason" and "verdict" keys.
            score (int): The score to be formatted and passed to the FaithfulnessTemplate.

        Returns:
            str: The reason generated based on the provided verdicts and score.
        """
        contradictions = [
            verdict["reason"]
            for verdict in verdicts
            if verdict["verdict"].strip().lower() == "no"
        ]
        prompt = FaithfulnessTemplate.generate_reason(
            contradictions=contradictions, score=format(score, ".2f")
        )
        reason_response = self.model(prompt)
        reason = self.trim_to_json(reason_response)
        return reason

    def run(self):
        """
        Run the function to generate truths, claims, verdicts, score, and result.
        Return a dictionary containing the response, context, score, threshold, is_passed,
        and evaluated_with. If include_reason is True, also include the reason in the result.
        """
        truths = self.generate_truths()
        claims = self.generate_claims()
        verdicts = self.generate_verdicts(claims, truths)
        score = self.generate_score(verdicts)

        result = {
            "response": self.answer,
            "context": self.retrieval_context,
            "score": score,
            "threshold": self.threshold,
            "is_passed": score >= self.threshold,
            "evaluated_with": {
                "model": self.model_name,
                "include_reason": self.include_reason,
            },
        }

        if self.include_reason:
            reason = self.generate_reason(verdicts, score)
            result["reason"] = reason

        return result


# if __name__ == "__main__":
#     response = "Paris, london"
#     context = ["Paris is the capital of France.", "london is a city"]
#     test_instance = FaithfulnessTest(response, context)
#     result = test_instance.run()
#     print(result)

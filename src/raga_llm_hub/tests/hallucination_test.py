"""
Implemtation of Hallucination Test
"""

import json

from .prompt_template import HallucinationTemplate


class HallucinationTest:
    def __init__(
        self,
        client,
        actual_output,
        contexts,
        include_reason=True,
        model="gpt-4",
        threshold=0.5,
        temperature=0,
    ):
        """
        Initializes the class instance with the provided parameters.

        Args:
            client: The client for the function.
            actual_output: The actual output of the function.
            contexts: The contexts for the function.
            include_reason: Whether to include the reason or not (default is True).
            model: The model to be used (default is "gpt-3.5-turbo").
            threshold: The threshold value for the function (default is 0.5).
            temperature: The temperature value for the function (default is 0).
        """
        self.actual_output = actual_output
        self.contexts = contexts
        self.include_reason = include_reason
        self.model_name = model
        self.threshold = threshold
        self.temperature = temperature
        self.client = client

    def model(self, prompt):
        """
        Create chat completions for a given prompt using the specified model, temperature, and messages.
        """
        return self.client.chat.completions.create(
            model=self.model_name,
            temperature=self.temperature,
            messages=[{"role": "system", "content": prompt}],
        )

    def trim_to_json(self, response):
        """
        Trim the given response to a JSON format.

        Args:
            self: The instance of the class.
            response: The response to be trimmed to JSON format.

        Returns:
            The response in JSON format.
        """
        message_content = response.choices[0].message.content
        data = json.dumps(message_content)
        return json.loads(data)

    def generate_verdicts(self):
        """
        Generate verdicts based on actual output and contexts using the model.
        """
        verdict_prompt = HallucinationTemplate.generate_verdicts(
            actual_output=self.actual_output, contexts=self.contexts
        )
        verdict_response = self.model(verdict_prompt)
        verdicts = json.loads(self.trim_to_json(verdict_response))["verdicts"]
        return verdicts

    def generate_score(self, verdicts):
        """
        Generate a score based on the given verdicts.

        Parameters:
            self: The object itself.
            verdicts: A list of verdicts containing the "verdict" key.

        Returns:
            float: The calculated score.
        """
        total = len(verdicts)
        hallucination_count = sum(
            1 for verdict in verdicts if verdict["verdict"].strip().lower() == "no"
        )
        score = hallucination_count / total
        return score

    def generate_reason(self, verdicts, score):
        """
        Generates a reason based on the given verdicts and score.

        Args:
            self: the object itself
            verdicts: a list of dictionaries containing verdicts and reasons
            score: a numerical value representing the score

        Returns:
            A reason generated based on the given verdicts and score.
        """
        factual_alignments = [
            verdict["reason"]
            for verdict in verdicts
            if verdict["verdict"].strip().lower() == "no"
        ]
        contradictions = [
            verdict["reason"]
            for verdict in verdicts
            if verdict["verdict"].strip().lower() != "no"
        ]
        prompt = HallucinationTemplate.generate_reason(
            factual_alignments=factual_alignments,
            contradictions=contradictions,
            score=format(score, ".2f"),
        )
        res = self.model(prompt)
        reason = self.trim_to_json(res)
        return reason

    def run(self):
        """
        Run the evaluation process and generate the result including actual output, contexts, score, threshold, pass status, and evaluation details.
        """
        verdicts = self.generate_verdicts()
        score = self.generate_score(verdicts)

        result = {
            "actual_output": self.actual_output,
            "contexts": self.contexts,
            "score": score,
            "threshold": self.threshold,
            "is_passed": score <= self.threshold,
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
#     actual_output = "paris, london"
#     contexts = ["Paris is the capital of France.", "London is a city"]

#     # Run the test
#     test_instance = HallucinationTest(actual_output, contexts)
#     result = test_instance.run()
#     print(result)

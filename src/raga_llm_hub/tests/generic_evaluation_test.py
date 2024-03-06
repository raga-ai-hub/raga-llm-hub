"""
Implementation of Generic Evaluation Test
"""

import json

from .prompt_template import GEvalTemplate


class GenericEvaluationTest:
    """
    Class to handle generic test metrics.
    """

    def __init__(
        self,
        client,
        metric_name,
        evaluation_criteria,
        input_text,
        actual_output,
        context,
        expected_output,
        model="gpt-3.5-turbo",
        threshold=0.5,
        temperature=0,
    ):
        """
        Initialize the GenericEvaluationTest instance.

        Args:
        - metric_name (str): Name of the metric.
        - evaluation_criteria (str): Criteria for evaluation.
        - input_text (str): Input text for the evaluation.
        - actual_output (str): Actual output to be evaluated.
        - context (list): Context for the evaluation.
        - expected_output (str): Expected output for the evaluation.
        - model (str): Model name to be used for evaluation (default is "gpt-3.5-turbo").
        - threshold (float): Threshold for success (default is 0.5).
        - temperature (int): Temperature parameter for model completion (default is 0).
        """
        self.metric_name = metric_name
        self.evaluation_criteria = evaluation_criteria
        self.input_text = input_text
        self.actual_output = actual_output
        self.context = context
        self.expected_output = expected_output
        self.model_name = model
        self.threshold = threshold
        self.temperature = temperature
        self.client = client

    def model(self, prompt):
        """
        Create chat completions using the specified model, temperature, and prompt messages.

        Parameters:
            prompt (str): The prompt message for chat completion.

        Returns:
            dict: The chat completions created by the model.
        """
        return self.client.chat.completions.create(
            model=self.model_name,
            temperature=self.temperature,
            messages=[{"role": "system", "content": prompt}],
        )

    def trim_to_json(self, response):
        """
        Trim the given response to JSON format.

        Args:
            self: The instance of the class.
            response: The response object to be trimmed to JSON format.

        Returns:
            The response data in JSON format.
        """
        message_content = response.choices[0].message.content
        data = json.dumps(message_content)
        return json.loads(data)

    def generate_evaluation_steps(self):
        """
        Generate evaluation steps based on the criteria.

        Returns:
        - list: Evaluation steps.
        """
        prompt = GEvalTemplate.evaluation_steps_template(
            criteria=self.evaluation_criteria
        )
        steps_response = self.model(prompt)
        steps = json.loads(self.trim_to_json(steps_response))["steps"]
        return steps

    def generate_evaluation_results(self, evaluation_steps):
        """
        Generate evaluation results based on the evaluation steps and the provided text data.

        Args:
        - evaluation_steps (list): Evaluation steps.

        Returns:
        - dict: Evaluation results.
        """
        text = {
            "input": self.input_text,
            "actual_output": self.actual_output,
            "context": self.context,
            "expected_output": self.expected_output,
        }
        prompt = GEvalTemplate.evaluation_results_template(
            evaluation_steps=evaluation_steps, text=text
        )
        results_response = self.model(prompt)
        results = json.loads(self.trim_to_json(results_response))
        return results

    def run(self):
        """
        Run the evaluation test and return the results.

        Returns:
        - dict: Test results.
        """
        evaluation_steps = self.generate_evaluation_steps()
        results = self.generate_evaluation_results(evaluation_steps)

        score = float(results["score"]) / 10
        reason = results["reason"]

        threshold = 0.5
        success = score >= threshold

        test_result = {
            "metric_name": self.metric_name,
            "evaluation_criteria": self.evaluation_criteria,
            "prompt": self.input_text,
            "actual_response": self.actual_output,
            "context": self.context,
            "expected_response": self.expected_output,
            "score": score,
            "threshold": self.threshold,
            "is_passed": success,
            "evaluated_with": {
                "model": self.model_name,
            },
            "reason": reason,
        }

        return test_result


# if __name__ == "__main__":
#     metric_name = "Coherence"  # name of metric
#     evaluation_criteria = (
#         "Coherence - determine if the actual output is coherent with the input."
#     )
#     input_text = "What is the capital of France?"
#     actual_output = "paris, london"
#     context = ["Paris is the capital of France.", "london is a city"]
#     expected_output = "Paris"

#     test_instance = GenericEvaluationTest(
#         metric_name,
#         evaluation_criteria,
#         input_text,
#         actual_output,
#         context,
#         expected_output,
#     )
#     result = test_instance.run()
#     print(result)

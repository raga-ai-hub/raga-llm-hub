"""
Contextual Precision Test
"""

import json

from .prompt_template import ContextualPrecisionTemplate


class ContextualPrecisionTest:
    """
    Class to perform contextual precision test.
    """

    def __init__(
        self,
        client,
        question,
        expected_output,
        retrieval_context,
        include_reason=True,
        model="gpt-3.5-turbo",
        threshold=0.5,
        temperature=0,
    ):
        """
        Initialize the ContextualPrecisionTest object.

        Args:
        question (str): The question to be asked.
        expected_output (str): The expected output for the question.
        retrieval_context (list): A list of strings representing the context for the question.
        include_reason (bool): Whether to include the reason for the test result. Default is True.
        model (str): The name of the OpenAI model to be used. Default is "gpt-3.5-turbo".
        threshold (float): The threshold for the test score. Default is 0.5.
        temperature (int): The temperature parameter for the model. Default is 0.
        """
        self.question = question
        self.expected_output = expected_output
        self.retrieval_context = retrieval_context
        self.include_reason = include_reason
        self.model_name = model
        self.threshold = threshold
        self.temperature = temperature
        self.client = client

    def model(self, prompt):
        """
        Generate model completions for the given prompt.

        Args:
        prompt (str): The prompt for which model completions are to be generated.

        Returns:
        dict: The model completion response.
        """
        return self.client.chat.completions.create(
            model=self.model_name,
            temperature=self.temperature,
            messages=[{"role": "system", "content": prompt}],
        )

    def trim_to_json(self, response):
        """
        Trim the model response to extract the JSON content.

        Args:
        response (dict): The model completion response.

        Returns:
        dict: The JSON content extracted from the model response.
        """
        message_content = response.choices[0].message.content
        data = json.dumps(message_content)
        return json.loads(data)

    def generate_verdicts(self):
        """
        Generate verdicts for the question using the retrieval context.

        Returns:
        list: A list of verdicts generated for the question.
        """
        verdict_prompt = ContextualPrecisionTemplate.generate_verdicts(
            self.question, self.expected_output, self.retrieval_context
        )
        verdict_response = self.model(verdict_prompt)
        verdicts = json.loads(self.trim_to_json(verdict_response))["verdicts"]
        return verdicts

    def generate_score(self, verdicts):
        """
        Generate the score for the test based on the generated verdicts.

        Args:
        verdicts (list): A list of verdicts generated for the question.

        Returns:
        float: The score for the test.
        """
        node_verdicts = [
            1 if v["verdict"].strip().lower() == "yes" else 0 for v in verdicts
        ]
        sum_weighted_precision_at_k = 0.0
        relevant_nodes_count = 0

        for k, is_relevant in enumerate(node_verdicts, start=1):
            if is_relevant:
                relevant_nodes_count += 1
                precision_at_k = relevant_nodes_count / k
                sum_weighted_precision_at_k += precision_at_k * is_relevant

        if relevant_nodes_count == 0:
            return 0

        weighted_cumulative_precision = (
            sum_weighted_precision_at_k / relevant_nodes_count
        )

        return weighted_cumulative_precision

    def generate_reason(self, score):
        """
        Generate the reason for the test result based on the score and verdicts.

        Args:
        score (float): The score for the test.

        Returns:
        dict: The reason for the test result.
        """
        prompt = ContextualPrecisionTemplate.generate_reason(
            input=self.question,
            verdicts=self.verdicts,
            score=format(score, ".2f"),
        )

        res = self.model(prompt)
        reason = self.trim_to_json(res)
        return reason

    def run(self):
        """
        Run the contextual precision test and return the result.

        Returns:
        dict: The result of the contextual precision test.
        """
        self.verdicts = self.generate_verdicts()
        score = self.generate_score(self.verdicts)

        result = {
            "prompt": self.question,
            "expected_response": self.expected_output,
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
            reason = self.generate_reason(score)
            result["reason"] = reason

        return result


# if __name__ == "__main__":
#     prompt = "What is the capital of France?"
#     expected_response = "paris"
#     context = ["Paris is the capital of France.", "london is a city"]

#     test_instance = ContextualPrecisionTest(prompt, expected_response, context)
#     result = test_instance.run()
#     print(result)

"""
Answer relevancy test for LLM
"""

import json

from .prompt_template import RelevancyTemplate


class RelevancyTest:
    def __init__(
        self,
        client,
        question,
        answer,
        retrieval_context,
        include_reason=True,
        model="gpt-3.5-turbo",
        threshold=0.5,
        temperature=0,
    ):
        """
        Initialize the RelevancyTest class with the given parameters.

        Args:
        question (str): The question to be evaluated.
        answer (str): The answer to the question.
        retrieval_context (list): The context or background information related to the question and answer.
        include_reason (bool, optional): Flag to indicate whether to include the reason for the evaluation. Defaults to True.
        model (str, optional): The OpenAI model to be used for evaluation. Defaults to "gpt-3.5-turbo".
        threshold (float, optional): The threshold for the evaluation score. Defaults to 0.5.
        temperature (int, optional): The temperature value for the OpenAI model. Defaults to 0.
        """
        self.answer = answer
        self.retrieval_context = retrieval_context
        self.question = question
        self.include_reason = include_reason
        self.model_name = model
        self.threshold = threshold
        self.temperature = temperature
        self.client = client

    def model(self, prompt):
        """
        Generate the model completion based on the provided prompt.

        Args:
        prompt (str): The prompt to be passed to the OpenAI model.

        Returns:
        dict: The response from the OpenAI model.
        """
        return self.client.chat.completions.create(
            model=self.model_name,
            temperature=self.temperature,
            messages=[{"role": "system", "content": prompt}],
        )

    def trim_to_json(self, response):
        """
        Convert the model response to a JSON format.

        Args:
        response (dict): The model response.

        Returns:
        dict: The JSON formatted response.
        """
        message_content = response.choices[0].message.content
        data = json.dumps(message_content)
        return json.loads(data)

    def generate_key_points(self):
        """
        Generate key points from the answer and retrieval context using the OpenAI model.

        Returns:
        list: The key points generated from the model response.
        """
        key_points_prompt = RelevancyTemplate.generate_key_points(
            self.answer, self.retrieval_context
        )
        key_points_response = self.model(key_points_prompt)
        data = json.loads(self.trim_to_json(key_points_response))
        key_points = data["key_points"]
        return key_points

    def generate_verdicts(self, key_points):
        """
        Generate verdicts based on the question and key points using the OpenAI model.

        Args:
        key_points (list): The key points generated from the answer and retrieval context.

        Returns:
        list: The verdicts generated from the model response.
        """
        verdict_prompt = RelevancyTemplate.generate_verdicts(self.question, key_points)
        verdict_response = self.model(verdict_prompt)
        verdicts = json.loads(self.trim_to_json(verdict_response))["verdicts"]
        return verdicts

    def generate_score(self, verdicts):
        """
        Generate the relevancy score based on the verdicts.

        Args:
        verdicts (list): The verdicts generated from the model response.

        Returns:
        float: The relevancy score.
        """
        if len(verdicts) == 0:
            return 0

        relevant_count = sum(
            1 for verdict in verdicts if verdict["verdict"].strip().lower() != "no"
        )
        return relevant_count / len(verdicts)

    def generate_reason(self, verdicts, key_points, score):
        """
        Generate the reason for the evaluation based on the verdicts, key points, and score.

        Args:
        verdicts (list): The verdicts generated from the model response.
        key_points (list): The key points generated from the answer and retrieval context.
        score (float): The relevancy score.

        Returns:
        dict: The reason for the evaluation.
        """
        for i, _ in enumerate(verdicts):
            verdicts[i]["key_point"] = key_points[i]

        irrelevant_points = [
            verdict["key_point"]
            for verdict in verdicts
            if verdict["verdict"].strip().lower() == "no"
        ]

        prompt = RelevancyTemplate.generate_reason(
            irrelevant_points=irrelevant_points,
            original_question=self.question,
            answer=self.answer,
            score=format(score, ".2f"),
        )

        res = self.model(prompt)
        reason = self.trim_to_json(res)
        return reason

    def run(self):
        """
        A function to run the evaluation process and generate a result including prompt, response, context, score, threshold, evaluation status, and the model used for evaluation.
        """
        key_points = self.generate_key_points()
        verdicts = self.generate_verdicts(key_points)
        score = self.generate_score(verdicts)

        result = {
            "prompt": self.question,
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
            reason = self.generate_reason(verdicts, key_points, score)
            result["reason"] = reason

        return result


# if __name__ == "__main__":
#     prompt = "What is the capital of France?"
#     response = "paris, london"
#     context = ["Paris is the capital of France.", "london is a city"]

#     test_instance = RelevancyTest(prompt, response, context)
#     result = test_instance.run()
#     print(result)

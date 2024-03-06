"""
Contextual Relevancy Test
"""

import json

from .prompt_template import ContextualRelevancyTemplate


class ContextualRelevancyTest:
    """
    Class for testing contextual relevancy of a question and retrieval context
    """

    def __init__(
        self,
        client,
        question,
        retrieval_context,
        include_reason=True,
        model="gpt-3.5-turbo",
        threshold=0.5,
        temperature=0,
    ):
        """
        Initialize the test instance with the provided parameters.

        Args:
        - question: str, the question to be evaluated for contextual relevancy
        - retrieval_context: list of str, the retrieval context for the question
        - include_reason: bool, whether to include the reason for the evaluation (default True)
        - model: str, the name of the OpenAI model to be used (default 'gpt-3.5-turbo')
        - threshold: float, the threshold for the relevancy score (default 0.5)
        - temperature: int, the temperature for model completion (default 0)
        """
        self.question = question
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
        - prompt: str, the prompt for which model completions are to be generated

        Returns:
        - dict, the model completions for the prompt
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
        - response: dict, the model response

        Returns:
        - dict, the JSON content extracted from the model response
        """
        message_content = response.choices[0].message.content
        data = json.dumps(message_content)
        return json.loads(data)

    def generate_verdicts(self):
        """
        Generate verdicts for the question and retrieval context.

        Returns:
        - list of dict, the generated verdicts
        """
        verdict_prompt = ContextualRelevancyTemplate.generate_verdicts(
            self.question, self.retrieval_context
        )
        verdict_response = self.model(verdict_prompt)
        verdicts = json.loads(self.trim_to_json(verdict_response))["verdicts"]
        return verdicts

    def generate_score(self, verdicts_list):
        """
        Generate the relevancy score based on the generated verdicts.

        Args:
        - verdicts_list: list of dict, the generated verdicts

        Returns:
        - float, the relevancy score
        """
        irrelevant_sentences = sum(
            1 for verdict in verdicts_list if verdict["verdict"].lower() == "no"
        )
        total_sentence_count = len(verdicts_list)

        if total_sentence_count == 0:
            return 0

        return (total_sentence_count - irrelevant_sentences) / total_sentence_count

    def generate_reason(self):
        """
        Generate the reason for the evaluation, if include_reason is True.

        Returns:
        - dict, the reason for the evaluation
        """
        if self.include_reason:
            irrelevant_sentences = []
            for index, verdict in enumerate(self.verdicts):
                if verdict["verdict"].strip().lower() == "no":
                    data = {"Node": index + 1, "Sentence": verdict["sentence"]}
                    irrelevant_sentences.append(data)

            prompt = ContextualRelevancyTemplate.generate_reason(
                input=self.question,
                irrelevant_sentences=irrelevant_sentences,
                score=format(self.score, ".2f"),
            )

            res = self.model(prompt)
            reason = self.trim_to_json(res)
            return reason

    def run(self):
        """
        Run the contextual relevancy test and return the result.

        Returns:
        - dict, the result of the contextual relevancy test
        """
        self.verdicts = self.generate_verdicts()
        self.score = self.generate_score(self.verdicts)

        result = {
            "prompt": self.question,
            "context": self.retrieval_context,
            "score": self.score,
            "threshold": self.threshold,
            "is_passed": self.score >= self.threshold,
            "evaluated_with": {
                "model": self.model_name,
                "include_reason": self.include_reason,
            },
        }

        if self.include_reason:
            reason = self.generate_reason()
            result["reason"] = reason

        return result


# if __name__ == "__main__":
#     prompt = "What is the capital of France?"
#     context = ["Paris is the capital of France.", "london is a city"]
#     test_instance = ContextualRelevancyTest(prompt, context)
#     result = test_instance.run()
#     print(result)

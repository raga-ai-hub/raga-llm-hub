"""
summarisation Test
"""

import json

from .prompt_template import summarisationTemplate


class SummarisationTest:
    """
    Class for conducting summarisation test.
    """

    def __init__(
        self,
        client,
        source_document,
        summary,
        model="gpt-3.5-turbo",
        threshold=0.5,
        temperature=0,
        n=5,  # no of questions to generate
    ):
        """
        Initialize the SummarisationTest instance with source document, summary, and other parameters.

        Args:
        source_document (str): The original document for summarisation.
        summary (str): The summary of the original document.
        n (int): Number of questions to generate.
        model (str): Name of the model to use for summarisation.
        threshold (float): Threshold for passing the summarisation test.
        temperature (int): Temperature parameter for the model.
        """
        self.source_document = source_document
        self.summary = summary
        self.n = n
        self.model_name = model
        self.threshold = threshold
        self.temperature = temperature
        self.client = client

    def model(self, prompt):
        """
        Generate model completions based on the given prompt.

        Args:
        prompt (str): Prompt for generating model completions.

        Returns:
        dict: Model completions response.
        """
        return self.client.chat.completions.create(
            model=self.model_name,
            temperature=self.temperature,
            messages=[{"role": "system", "content": prompt}],
        )

    def trim_to_json(self, response):
        """
        Trim the model response to JSON format.

        Args:
        response (dict): Model response.

        Returns:
        dict: Trimmed JSON response.
        """
        message_content = response.choices[0].message.content
        data = json.dumps(message_content)
        return json.loads(data)

    def generate_questions(self, score_type):
        """
        Generate questions based on the score type.

        Args:
        score_type (str): Type of score for generating questions.

        Returns:
        list: List of generated questions.
        """
        if score_type == "alignment":
            prompt = summarisationTemplate.closed_end_questions_template(
                n=self.n, text=self.summary
            )
        elif score_type == "inclusion":
            prompt = summarisationTemplate.closed_end_questions_template(
                n=self.n, text=self.source_document
            )

        res = self.model(prompt)
        json_output = self.trim_to_json(res)
        data = json.loads(json_output)
        return data["questions"]

    def get_answer(self, question, text):
        """
        Get answer for a given question and text.

        Args:
        question (str): Question to get answer for.
        text (str): Text to search for the answer.

        Returns:
        str: Answer for the question.
        """
        prompt = summarisationTemplate.closed_end_answers_template(
            question=question, text=text
        )
        res = self.model(prompt)
        reason = self.trim_to_json(res)
        return reason

    def get_score(self, score_type):
        """
        Get the score based on the score type.

        Args:
        score_type (str): Type of score for getting the score.

        Returns:
        float: Calculated score.
        """
        questions = []
        if score_type == "alignment":
            questions = self.generate_questions(score_type)
        elif score_type == "inclusion":
            questions = self.generate_questions(score_type)

        score = 0
        interval = 1 / len(questions)
        for question in questions:
            source_answer = self.get_answer(question, self.source_document)
            summary_answer = self.get_answer(question, self.summary)

            if source_answer.strip().lower() == summary_answer.strip().lower():
                score += interval
        return score

    def run(self):
        """
        Run the summarisation test and calculate the score.

        Returns:
        dict: Test result including prompt, response, score, threshold, and evaluation details.
        """
        alignment_score = self.get_score("alignment")
        inclusion_score = self.get_score("inclusion")
        summarisation_score = min(alignment_score, inclusion_score)

        result = {
            "prompt": self.source_document,
            "response": self.summary,
            "score": summarisation_score,
            "threshold": self.threshold,
            "is_passed": summarisation_score >= self.threshold,
            "evaluated_with": {
                "model": self.model_name,
                "n": self.n,
            },
        }

        return result


# if __name__ == "__main__":
#     prompt = """
# The 'inclusion score' is calculated as the percentage of assessment questions
# for which both the summary and the original document provide a 'yes' answer. This
# method ensures that the summary not only includes key information from the original
# text but also accurately represents it. A higher inclusion score indicates a
# more comprehensive and faithful summary, signifying that the summary effectively
# encapsulates the crucial points and details from the original content.
# """
#     response = """
# The inclusion score quantifies how well a summary captures and
# accurately represents key information from the original text,
# with a higher score indicating greater comprehensiveness.
# """
#     test_instance = SummarisationTest(prompt, response)
#     result = test_instance.run()
#     print(result)

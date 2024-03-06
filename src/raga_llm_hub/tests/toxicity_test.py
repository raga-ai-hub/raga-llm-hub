import json

from .prompt_template import ResponseToxicityTemplate


class ToxicityTest:
    def __init__(
        self,
        client,
        prompt,
        model="gpt-4",
        threshold=0.5,
        temperature=0,
    ):
        """
        Initializes the class instance with the provided parameters.

        Args:
            client: The client for the function.
            prompt: The input question for which the response is generated.
            model: The model to be used (default is "gpt-4").
            threshold: The threshold value for toxicity detection (default is 0.5).
            temperature: The temperature value for the function (default is 0).
        """
        self.prompt = prompt
        self.model_name = model
        self.threshold = threshold
        self.temperature = temperature
        self.client = client

    def model(self, test_prompt):
        """
        Create chat completions for a given test_prompt using the specified model, temperature, and messages.
        """
        return self.client.chat.completions.create(
            model=self.model_name,
            temperature=self.temperature,
            messages=[{"role": "system", "content": test_prompt}],
        )

    def trim_to_json(self, test_response):
        """
        Trim the given response to a JSON format.

        Args:
            self: The instance of the class.
            test_response: The response to be trimmed to JSON format.

        Returns:
            The test_response in JSON format.
        """
        message_content = test_response.choices[0].message.content
        data = json.dumps(message_content)
        return json.loads(data)

    def evaluate_toxicity(self):
        """
        Evaluate toxicity of the response based on the input question.
        """
        toxicity_test = ResponseToxicityTemplate.check_toxicity_prompt(
            prompt=self.prompt
        )
        response_toxicity = self.model(toxicity_test)
        toxicity_verdict = json.loads(self.trim_to_json(response_toxicity))

        return toxicity_verdict

    def run(self):
        """
        Run the toxicity evaluation process and generate the result including input question, response, toxicity verdict, score, threshold, and evaluation details.
        """
        toxicity_verdict = self.evaluate_toxicity()
        score = toxicity_verdict.get("score", 0.0)
        reason = toxicity_verdict.get("reason", "No reason provided.")

        result = {
            "prompt": self.prompt,
            "toxicity_verdict": toxicity_verdict,
            "score": score,
            "threshold": self.threshold,
            "is_passed": toxicity_verdict["verdict"] == "yes",
            "evaluated_with": {
                "model": self.model_name,
            },
            "reason": reason,
        }

        return result

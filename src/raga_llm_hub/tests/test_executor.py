"""
Container code for all the test runners
"""

import json

from ..guardrails import (
    NSFW,
    Anonymize,
    BanCompetitors,
    BanSubstrings,
    BanTopics,
    Code,
    Deanonymize,
    FactualConsistency,
    Gibberish,
    InvisibleText,
    JSONVerify,
    Language,
    LanguageSame,
    MaliciousURLs,
    NoRefusal,
    Politeness,
    Profanity,
    ReadingTime,
    Regex,
    Secrets,
    Sensitive,
    Sentiment,
    TokenLimit,
    URLReachability,
    ValidCsv,
    ValidSql,
    Vault,
)
from . import (
    BiasTest,
    CoherenceTest,
    ConcisenessTest,
    ContextualPrecisionTest,
    ContextualRecallTest,
    ContextualRelevancyTest,
    CorrectnessTest,
    CostTest,
    FaithfulnessTest,
    GenericEvaluationTest,
    HallucinationTest,
    HarmlessTest,
    LatencyTest,
    PromptInjectionTest,
    RelevancyTest,
    ResponseToxicityTest,
    SummarisationTest,
    ToxicityTest,
    chunk_impact_test,
    complexity_test,
    consistency_test,
    context_retrieval_metrics_test,
    cosine_similarity_test,
    cover_test,
    dan_vulnerability_scanner,
    grade_score_test,
    ir_metrics_test,
    length_test,
    lmrc_vulnerability_scanner,
    maliciousness_test,
    overall_test,
    pos_test,
    prompt_injection_test,
    readability_test,
    refusal_test,
    sentiment_analysis_test,
    winner_test,
)

temp_vault = Vault()


# pylint: disable=too-many-public-methods
class TestExecutor:
    """
    Container class for the all the tests supported.
    """

    def __init__(self, openai_client=None):
        """
        Initializes a new instance of the class with an optional OpenAI client.

        Parameters:
            openai_client (optional): The OpenAI client to use.

        Returns:
            None
        """
        self.client = openai_client

    def run_relevancy_test(self, test_data):
        """
        Run an relevancy test using the given test data.

        Parameters:
            self: the object itself
            test_data (dict): a dictionary containing the prompt, response, context, model, include_reason, and threshold

        Returns:
            The result of the relevancy test.
        """
        # TODO: Check of the parameters are valid

        res = RelevancyTest(
            client=self.client,
            question=test_data["prompt"],
            answer=test_data["response"],
            retrieval_context=test_data["context"],
            model=test_data["test_arguments"].get("model", "gpt-3.5-turbo"),
            include_reason=test_data["test_arguments"].get("include_reason", True),
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        ).run()

        # TODO: Check if the results are in the desired form
        return res

    def run_contextual_precision_test(self, test_data):
        """
        A function to run a contextual precision test.

        Args:
            self: The object itself.
            test_data (dict): A dictionary containing the test data with keys:
                - "prompt": The prompt for the test.
                - "expected_response": The expected response for the test.
                - "context": The context for the test.
                - "model" (optional): The model for the test (default is "gpt-3.5-turbo").
                - "include_reason" (optional): Whether to include the reason for the result (default is True).
                - "threshold" (optional): The threshold for the test (default is 0.5).

        Returns:
            The result of the contextual precision test.
        """
        # CHECKING: if the required parameters are not present raise error(If the required parameters are not present, by default it does not give any error and provide the score as 0; only gives error if none of the 4 parameters are given)
        if test_data["prompt"] is None:
            raise ValueError("prompt is required for contextual_precision_test")
        if test_data["expected_response"] is None:
            raise ValueError(
                "expected_response is required for contextual_precision_test"
            )
        if test_data["context"] is None:
            raise ValueError("context is required for contextual_precision_test")

        # TODO: Check of the parameters are valid;(they are valid- CHECKED)
        res = ContextualPrecisionTest(
            client=self.client,
            question=test_data["prompt"],
            expected_output=test_data["expected_response"],
            retrieval_context=test_data["context"],
            model=test_data["test_arguments"].get("model", "gpt-3.5-turbo"),
            include_reason=test_data["test_arguments"].get("include_reason", True),
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        ).run()

        # TODO: Check if the results are in the desired form
        return res

    def run_contextual_recall_test(self, test_data):
        """
        A function to run contextual recall test.

        Args:
            self: The object itself.
            test_data (dict): A dictionary containing test data with the following keys:
                - expected_response (str): The expected response text.
                - context (str): The context for the test.
                - model (str, optional): The model to use for the test. Defaults to "gpt-3.5-turbo".
                - include_reason (bool, optional): Whether to include reason in the test. Defaults to True.
                - threshold (float, optional): The threshold for the test. Defaults to 0.5.

        Returns:
            The result of the contextual recall test.
        """

        # CHECKING: if the required parameters are not present raise error(If the required parameters are not present, by default it does not give any error and provide the score as 0; only gives error if none of the 4 parameters are given)
        if test_data["expected_response"] is None:
            raise ValueError("expected_response is required for contextual_recall_test")
        if test_data["context"] is None:
            raise ValueError("context is required for contextual_recall_test")

        # TODO: Check of the parameters are valid;(they are valid- CHECKED)
        res = ContextualRecallTest(
            client=self.client,
            expected_output=test_data["expected_response"],
            retrieval_context=test_data["context"],
            model=test_data["test_arguments"].get("model", "gpt-3.5-turbo"),
            include_reason=test_data["test_arguments"].get("include_reason", True),
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        ).run()

        # TODO: Check if the results are in the desired form
        return res

    def run_contextual_relevancy_test(self, test_data):
        """
        A function to run a contextual relevancy test using the given test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing the test data with keys "prompt", "context", "model", "include_reason", and "threshold"

        Returns:
            The result of the contextual relevancy test
        """
        # CHECKING: if the required parameters are not present raise error(If the required parameters are not present, by default it does not give any error and provide the score as 0; only gives error if none of the 4 parameters are given)
        if test_data["prompt"] is None:
            raise ValueError("prompt is required for contextual_relevancy_test")
        if test_data["context"] is None:
            raise ValueError("context is required for contextual_relevancy_test")

        # TODO: Check of the parameters are valid;(they are valid- CHECKED)
        res = ContextualRelevancyTest(
            client=self.client,
            question=test_data["prompt"],
            retrieval_context=test_data["context"],
            model=test_data["test_arguments"].get("model", "gpt-3.5-turbo"),
            include_reason=test_data["test_arguments"].get("include_reason", True),
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        ).run()

        # TODO: Check if the results are in the desired form
        return res

    def run_faithfulness_test(self, test_data):
        """
        A function to run a faithfulness test on the given test data.

        Args:
            self: The object itself.
            test_data (dict): A dictionary containing the test data with the following keys:
                - "response": The response for the test.
                - "context": The context for the test.
                - "model" (optional): The model for the test. Defaults to "gpt-3.5-turbo".
                - "include_reason" (optional): Whether to include reason in the test. Defaults to True.
                - "threshold" (optional): The threshold for the test. Defaults to 0.5.

        Returns:
            The result of the faithfulness test.
        """
        # TODO: Check of the parameters are valid

        res = FaithfulnessTest(
            client=self.client,
            answer=test_data["response"],
            retrieval_context=test_data["context"],
            model=test_data["test_arguments"].get("model", "gpt-3.5-turbo"),
            include_reason=test_data["test_arguments"].get("include_reason", True),
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        ).run()

        # TODO: Check if the results are in the desired form
        return res

    def run_maliciousness_test(self, test_data):
        """
        Run a summarisation test using the provided test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing prompt, response, model, and threshold.

        Returns:
            The result of the summarisation test.
        """
        # TODO: Check of the parameters are valid

        res = maliciousness_test(
            client=self.client,
            prompt=test_data["prompt"],
            response=test_data["response"],
            context=test_data["context"],
            model=test_data["test_arguments"].get("model", "gpt-4"),
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        )

        # TODO: Check if the results are in the desired form
        return res

    def run_summarisation_test(self, test_data):
        """
        Run a summarisation test using the provided test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing prompt, response, model, and threshold.

        Returns:
            The result of the summarisation test.
        """
        # TODO: Check of the parameters are valid

        res = SummarisationTest(
            client=self.client,
            source_document=test_data["prompt"],
            summary=test_data["response"],
            model=test_data["test_arguments"].get("model", "gpt-3.5-turbo"),
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        ).run()

        # TODO: Check if the results are in the desired form
        return res

    def run_prompt_injection_test(self, test_data):
        """
        Run prompt injection test using the given test data.

        Parameters:
            self: the object itself
            test_data (dict): a dictionary containing the prompt and threshold

        Returns:
            The result of the prompt injection test.
        """
        # TODO: Check of the parameters are valid

        res = prompt_injection_test(
            prompt=test_data["prompt"],
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        )

        # TODO: Check if the results are in the desired form
        return res

    def run_sentiment_analysis_test(self, test_data):
        """
        Run sentiment analysis test using the given test data.

        Parameters:
            self: the object itself
            test_data (dict): a dictionary containing the response and threshold

        Returns:
            The result of the response sentiment test.
        """

        if test_data["response"] is None:
            raise ValueError("response is required for sentiment_analysis_test")

        res = sentiment_analysis_test(
            response=test_data["response"],
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        )

        # TODO: Check if the results are in the desired form
        return res

    def run_toxicity_test(self, test_data):
        """
        Run toxicity test using the given test data.

        Parameters:
            self: the object itself
            test_data (dict): a dictionary containing the response and threshold

        Returns:
            The result of the response toxicity test.
        """
        # Check if prompt is available
        if test_data["prompt"] is None:
            raise ValueError("prompt is required for toxicity_test")

        res = ToxicityTest(
            client=self.client,
            prompt=test_data["prompt"],
            model=test_data["test_arguments"].get("model", "gpt-4"),
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        ).run()

        # TODO: Check if the results are in the desired form
        return res

    def run_conciseness_test(self, test_data):
        """
        A method to run a conciseness test using the given test data.

        Args:
            test_data (dict): A dictionary containing the prompt, response, model, and strictness.

        Returns:
            The result of the conciseness test.
        """

        # TODO: Check of the parameters are valid

        res = ConcisenessTest(
            client=self.client,
            prompt=test_data["prompt"],
            response=test_data["response"],
            context=test_data["context"],
            model=test_data["test_arguments"].get("model", "gpt-4"),
            strictness=test_data["test_arguments"].get("strictness", 1),
        ).run()

        # TODO: Check if the results are in the desired form
        return res

    def run_coherence_test(self, test_data):
        """
        A function to run a coherence test using the provided test data.

        Parameters:
            self: the object instance
            test_data: a dictionary containing the prompt, response, and test arguments

        Returns:
            The result of the coherence test.
        """

        # TODO: Check of the parameters are valid

        res = CoherenceTest(
            client=self.client,
            prompt=test_data["prompt"],
            response=test_data["response"],
            context=test_data["context"],
            model=test_data["test_arguments"].get("model", "gpt-3.5-turbo"),
            strictness=test_data["test_arguments"].get("strictness", 1),
        ).run()

        # TODO: Check if the results are in the desired form
        return res

    def run_consistency_test(self, test_data):
        """
        A function to run a consistency test on the given test data.

        Args:
            self: The object itself.
            test_data (dict): A dictionary containing the test data with the following keys:
                - prompt (str): The prompt given to the model.
                - response (str): The model's response to the prompt.
                - num_samples(int) :  Number of samples to generate to check consistency.
                - model (str): The name of the model being evaluated (default is "gpt-3.5-turbo").
                - threshold(float): The threshold score above this the prompt will be flagged as injection prompt.

        Returns:
            The result of the consistency test.
        """

        # Check
        if test_data["prompt"] is None:
            raise ValueError("prompt is required for consistency_test")
        if test_data["response"] is None:
            raise ValueError("response is required for consistency_test")

        prompt = test_data["prompt"]
        response = test_data["response"]
        if isinstance(prompt, list):
            prompt = str(prompt)
        if isinstance(response, list):
            response = str(response)

        res = consistency_test(
            prompt=prompt,
            response=test_data["response"],
            num_samples=test_data["test_arguments"].get("num_samples", 5),
            model=test_data["test_arguments"].get("model", "gpt-4"),
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        )

        # TODO: Check if the results are in the desired form
        return res

    def run_cover_test(self, test_data):
        """
        Run a cover_test using the provided test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing response, concept set.

        Returns:
            The result of the cover test.
        """
        # TODO: Check of the parameters are valid

        res = cover_test(
            response=test_data["response"],
            concept_set=test_data["concept_set"],
        )

        # TODO: Check if the results are in the desired form
        return res

    def run_pos_test(self, test_data):
        """
        Run a pos_test using the provided test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing response, concept set.

        Returns:
            The result of the pos test.
        """
        # TODO: Check of the parameters are valid

        res = pos_test(
            response=test_data["response"],
            concept_set=test_data["concept_set"],
        )

        # TODO: Check if the results are in the desired form
        return res

    def run_length_test(self, test_data):
        """
        Run a length_test using the provided test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing response.

        Returns:
            The result of the length test.
        """
        # TODO: Check of the parameters are valid

        res = length_test(
            response=test_data["response"],
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        )

        # TODO: Check if the results are in the desired form
        return res

    def run_winner_test(self, test_data):
        """
        Run a winner_test using the provided test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing response, ground_truth, concept_set, model, temperature, max_tokens.


        Returns:
            The result of the winner test.
        """
        # TODO: Check of the parameters are valid

        res = winner_test(
            client=self.client,
            model_a_response=test_data["response"],
            model_b_response=test_data["expected_response"],
            concept_set=test_data["concept_set"],
            model=test_data["test_arguments"].get("model", "gpt-3.5-turbo"),
            temperature=test_data["test_arguments"].get("temperature", 0),
            max_tokens=test_data["test_arguments"].get("max_tokens", 512),
        )

        # TODO: Check if the results are in the desired form
        return res

    def run_overall_test(self, test_data):
        """
        Run a overall_test using the provided test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing response, ground_truth, concept_set, model, temperature, max_tokens.


        Returns:
            The result of the overall test.
        """
        # TODO: Check of the parameters are valid

        res = overall_test(
            client=self.client,
            response=test_data["response"],
            expected_response=test_data["expected_response"],
            concept_set=test_data["concept_set"],
            model=test_data["test_arguments"].get("model", "gpt-3.5-turbo"),
            temperature=test_data["test_arguments"].get("temperature", 0),
            max_tokens=test_data["test_arguments"].get("max_tokens", 512),
        )

        # TODO: Check if the results are in the desired form
        return res

    def run_refusal_test(self, test_data):
        """
        Run a refusal_test using the provided test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing response, threshold.

        Returns:
            The result of the refusal test.
        """
        # TODO: Check of the parameters are valid
        res = refusal_test(
            response=test_data["response"],
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        )
        # TODO: Check if the results are in the desired form
        return res

    def run_correctness_test(self, test_data):
        """
        Run an answer correctness test using the given test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing the test data with keys "prompt", "response", "expected_response", "context", "model", and "threshold".
        Returns:
            The result of the correctness test.
        """

        # TODO: Check of the parameters are valid
        res = CorrectnessTest(
            client=self.client,
            prompt=test_data["prompt"],
            response=test_data["response"],
            expected_response=test_data["expected_response"],
            context=test_data["context"],
            model=test_data["test_arguments"].get("model", "gpt-3.5-turbo"),
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        ).run()

        return res

    def run_generic_evaluation_test(self, test_data):
        """
        Run a generic test using the provided test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing metric_name, evaluation_criteria, prompt, response, context and expected_response.


        Returns:
            The result of the evaluation test.
        """
        # TODO: Check if the parameters are valid

        res = GenericEvaluationTest(
            client=self.client,
            input_text=test_data["prompt"],
            actual_output=test_data["response"],
            context=test_data["context"],
            expected_output=test_data["expected_response"],
            metric_name=test_data["test_arguments"].get("metric_name"),
            evaluation_criteria=test_data["test_arguments"].get("evaluation_criteria"),
            model=test_data["test_arguments"].get("model", "gpt-3.5-turbo"),
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        ).run()

        # TODO: Check if the results are in the desired form
        return res

    def run_hallucination_test(self, test_data):
        """
        Run a hallucination test using the provided test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing actual_output, contexts, model, include_reason, and threshold.

        Returns:
            The result of the hallucination test.
        """

        res = HallucinationTest(
            client=self.client,
            actual_output=test_data["response"],
            contexts=test_data["context"],
            model=test_data["test_arguments"].get("model", "gpt-3.5-turbo"),
            include_reason=test_data["test_arguments"].get("include_reason", True),
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        ).run()

        return res

    def run_bias_test(self, test_data):
        """
        Run a bias test using the provided test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing response, and threshold.

        Returns:
            The result of the bias test.
        """

        res = BiasTest(
            response=test_data["response"],
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        ).run()

        return res

    def run_response_toxicity_test(self, test_data):
        """
        Run a response toxicity test using the provided test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing response, and threshold.

        Returns:
            The result of the response toxicity test.
        """

        res = ResponseToxicityTest(
            client=self.client,
            prompt=test_data["prompt"],
            response=test_data["response"],
            model=test_data["test_arguments"].get("model", "gpt-4"),
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        ).run()

        return res

    def run_readability_test(self, test_data):
        """
        Run a readability score test using the given test data.

        Args:
            self: the object instance
            test_data (dict): A dictionary containing prompt, response, threshold
        Returns:
            The readability score
        """
        res = readability_test(
            prompt=test_data["prompt"],
            response=test_data["response"],
            threshold=test_data["test_arguments"].get("threshold", 5),
        )

        return res

    def run_cosine_similarity_test(self, test_data):
        """
        Run a cosine similarity test using the given test data.

        Args:
            self: the object instance
            test_data (dict): A dictionary containing prompt, response, threshold
        Returns:
            The cosine similarity score
        """
        res = cosine_similarity_test(
            client=self.client,
            prompt=test_data["prompt"],
            response=test_data["response"],
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        )

        return res

    def run_grade_score_test(self, test_data):
        """
        Run a grade score test using the given test data.

        Args:
            self: the object instance
            test_data (dict): A dictionary containing prompt, response, threshold
        Returns:
            The grade score
        """
        res = grade_score_test(
            prompt=test_data["prompt"],
            response=test_data["response"],
            threshold=test_data["test_arguments"].get("threshold", 5),
        )

        return res

    def run_complexity_test(self, test_data):
        """
        Run a complexity test using the given test data.

        Args:
            self: the object instance
            test_data(dict): A dictionary containing prompt, response, threshold
        Returns:
            The complexity score
        """
        res = complexity_test(
            prompt=test_data["prompt"],
            response=test_data["response"],
            threshold=test_data["test_arguments"].get("threshold", 5),
        )

        return res

    def run_cost_test(self, test_data):
        """
        Run a cost test with the given test data."""
        if test_data["cost"] is None:
            raise ValueError("cost is required for cost_test")

        res = CostTest(
            cost=test_data["cost"],
            threshold=test_data["test_arguments"].get("threshold", 0.4),
        ).run()
        return res

    def run_prompt_injection_modeleval_test(self, test_data):
        """
        Run a prompt injection modeleval test using the provided test data.

        Args:
            test_data (dict): The test data containing the cost and test arguments.

        Returns:
            The result of the cost test.
        """
        model_evaluator = PromptInjectionTest()
        res = model_evaluator.evaluate_single_model(
            client=self.client,
            model_name=test_data["test_arguments"].get(
                "model_name", "gpt-3.5-turbo-instruct"
            ),
            threshold=test_data["test_arguments"].get("threshold", 50),
            temperature=test_data["test_arguments"].get("temperature", 0),
            max_tokens=test_data["test_arguments"].get("max_tokens", 512),
        )

        return res

    def run_latency_test(self, test_data):
        """
        Run a latency test with the given test data.

        Parameters:
            self: The object instance
            test_data: The test data containing latency and test arguments

        Returns:
            res: The result of the latency test
        """
        if test_data["latency"] is None:
            raise ValueError("latency is required for latency_test")

        res = LatencyTest(
            latency=test_data["latency"],
            threshold=test_data["test_arguments"].get("threshold", 10.0),
        ).run()

        return res

    def run_harmless_test(self, test_data):
        """
        Run a harmless test using the provided test data.

        Args:
            test_data: A dictionary containing the test data, including the response and test arguments.

        Returns:
            The result of running the harmless test.
        """
        if test_data["response"] is None:
            raise ValueError("response is required for harmless_test")

        res = HarmlessTest(
            client=self.client,
            response=test_data["response"],
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        ).run()

        return res

    def run_prompt_injection_modelcompare_test(self, test_data):
        """
        Run a prompt injection modelcompare test using the provided test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing model name and other optional args to use for evaluation,
            threshold to apply

        Returns:
            The result of the evaluation test.

        """
        # with SuppressOutput():
        model_evaluator = PromptInjectionTest()
        res = model_evaluator.compare_models(
            client=self.client,
            model_name_a=test_data["test_arguments"].get(
                "model_name_a", "gpt-3.5-turbo-instruct"
            ),
            model_name_b=test_data["test_arguments"].get("model_name_b", "davinci-002"),
            temperature=test_data["test_arguments"].get("temperature", 0),
            max_tokens=test_data["test_arguments"].get("max_tokens", 512),
        )

        return res

    def run_chunk_impact_test(self, test_data):
        """
        Run a chunk impact test using the provided test data.

        Args:
            test_data: A dictionary containing the test data, including the response,context and test arguments.

        Returns:
            The result of context score and minimum context required to get similar response
        """

        if test_data["context"] is None:
            raise ValueError("context is required for Chunk Impact Test")

        context = test_data["context"]
        if isinstance(context, str):
            context = json.loads(context)

        # if context is a list of strings, convert it to list of lists
        if isinstance(context[0], str):
            context = [[x] for x in context]

        res = chunk_impact_test(
            contexts=test_data["context"],
            response=test_data["response"],
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        )

        return res

    def run_ir_metrics_test(self, test_data):
        if test_data["prompt"] is None:
            raise ValueError("prompt is required for ir_metrics_test")
        if test_data["context"] is None:
            raise ValueError("context is required for ir_metrics_test")
        res = ir_metrics_test(
            client=self.client,
            prompt=test_data["prompt"],
            retrieved_context=test_data["context"],
            metric_name=test_data["test_arguments"].get("metric_name", "Accuracy"),
            threshold=test_data["test_arguments"].get("threshold", 0.5),
            rel=test_data["test_arguments"].get("rel", None),
            cutoff=test_data["test_arguments"].get("cutoff", None),
            min_rel=test_data["test_arguments"].get("min_rel", None),
            max_rel=test_data["test_arguments"].get("max_rel", None),
            p=test_data["test_arguments"].get("p", None),
            normalize=test_data["test_arguments"].get("normalize", None),
            T=test_data["test_arguments"].get("T", None),
            recall=test_data["test_arguments"].get("recall", None),
            alpha=test_data["test_arguments"].get("alpha", None),
            judged_only=test_data["test_arguments"].get("judged_only", None),
            dcg=test_data["test_arguments"].get("dcg", None),
            gains=test_data["test_arguments"].get("gains", None),
            beta=test_data["test_arguments"].get("beta", None),
            relative=test_data["test_arguments"].get("relative", None),
            model=test_data["test_arguments"].get("model", "gpt-3.5-turbo"),
        )

        return res

    def run_context_retrieval_metrics_test(self, test_data):

        res = context_retrieval_metrics_test(
            expected_context=test_data["expected_context"],
            context=test_data["context"],
            metric_name=test_data["test_arguments"].get("metric_name"),
            threshold=test_data["test_arguments"].get("threshold", 0.6),
            relevance_threshold=test_data["test_arguments"].get(
                "relevance_threshold", 0.9
            ),
            k=test_data["test_arguments"].get("k", None),
        )

        return res

    def run_anonymize_guardrail(self, test_data):
        """
        Run an anonymize guardrail using the given test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing the response, and threshold.

        Returns:
            The result of the anonymize guardrail.
        """
        res = Anonymize(
            prompt=test_data["prompt"],
            vault=temp_vault,
            hidden_names=test_data["test_arguments"].get("hidden_names", []),
            allowed_names=test_data["test_arguments"].get("allowed_names", []),
            entity_types=test_data["test_arguments"].get("entity_types", []),
            use_faker=test_data["test_arguments"].get("use_faker", False),
            use_onnx=test_data["test_arguments"].get("use_onnx", False),
            threshold=test_data["test_arguments"].get("threshold", 0),
            language=test_data["test_arguments"].get("language", "en"),
        ).run()

        return res

    def run_deanonymize_guardrail(self, test_data):
        """
        Run an anonymize guardrail using the given test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing the response, and threshold.

        Returns:
            The result of the anonymize guardrail.
        """
        res = Deanonymize(
            prompt=test_data["prompt"],
            vault=temp_vault,
            matching_strategy=test_data["test_arguments"].get(
                "matching_strategy", "exact"
            ),
        ).run()

        return res

    def run_ban_competitors_guardrail(self, test_data):
        """
        Run a ban competitors guardrail using the given test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing the response, and threshold.

        Returns:
            The result of the ban competitors guardrail.
        """
        res = BanCompetitors(
            prompt=test_data["prompt"],
            competitors=test_data["test_arguments"].get("competitors", []),
            threshold=test_data["test_arguments"].get("threshold", 0.5),
            redact=test_data["test_arguments"].get("redact", True),
            model=test_data["test_arguments"].get("model", None),
        ).run()

        return res

    def run_ban_substrings_guardrail(self, test_data):
        """
        Run a ban substrings guardrail using the given test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing the response, and threshold.

        Returns:
        The result of the ban substrings guardrail.
        """
        res = BanSubstrings(
            prompt=test_data["prompt"],
            substrings=test_data["test_arguments"].get("substrings", []),
            match_type=test_data["test_arguments"].get("match_type", "str"),
            case_sensitive=test_data["test_arguments"].get("case_sensitive", False),
            redact=test_data["test_arguments"].get("redact", True),
            contains_all=test_data["test_arguments"].get("contains_all", False),
        ).run()

        return res

    def run_ban_topics_guardrail(self, test_data):
        """
        Run a ban topics guardrail using the given test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing the response, and threshold.

        Returns:
        The result of the ban topics guardrail.
        """
        res = BanTopics(
            prompt=test_data["prompt"],
            topics=test_data["test_arguments"].get("topics", []),
            threshold=test_data["test_arguments"].get("threshold", 0.6),
            model=test_data["test_arguments"].get("model", None),
            use_onnx=test_data["test_arguments"].get("use_onnx", False),
        ).run()

        return res

    def run_code_guardrail(self, test_data):
        """
        Run a code guardrail using the given test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing the response, and threshold.

        Returns:
        The result of the code guardrail.
        """
        res = Code(
            prompt=test_data["prompt"],
            languages=test_data["test_arguments"].get("languages", []),
            is_blocked=test_data["test_arguments"].get("is_blocked", True),
            threshold=test_data["test_arguments"].get("threshold", 0.5),
            use_onnx=test_data["test_arguments"].get("use_onnx", False),
        ).run()

        return res

    def run_factual_consistency_guardrail(self, test_data):
        """
        Run a factual consistency guardrail using the given test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing the response, and threshold.

        Returns:
        The result of the factual consistency guardrail.
        """
        res = FactualConsistency(
            prompt=test_data["prompt"],
            response=test_data["response"],
            threshold=test_data["test_arguments"].get("threshold", 0.5),
            use_onnx=test_data["test_arguments"].get("use_onnx", False),
        ).run()

        return res

    def run_invisible_text_guardrail(self, test_data):
        """
        Run an invisible text guardrail using the given test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing the response, and threshold.

        Returns:
        The result of the invisible text guardrail.
        """

        # If prompt is list convert it to string
        if len(test_data["prompt"]) > 1:
            print("More than one strings found! Only one string is expected.")
            test_data["prompt"] = test_data["prompt"][0]

        if isinstance(test_data["prompt"], list):
            test_data["prompt"] = str(test_data["prompt"])

        res = InvisibleText(
            prompt=test_data["prompt"],
        ).run()

        return res

    def run_language_guardrail(self, test_data):
        """
        Run a language guardrail using the given test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing the response, and threshold.

        Returns:
        The result of the language guardrail.
        """
        if isinstance(test_data["prompt"], list):
            test_data["prompt"] = str(test_data["prompt"])

        res = Language(
            prompt=test_data["prompt"],
            valid_languages=test_data["test_arguments"].get("valid_languages", ["en"]),
            threshold=test_data["test_arguments"].get("threshold", 0.6),
            match_type=test_data["test_arguments"].get("match_type", "full"),
            use_onnx=test_data["test_arguments"].get("use_onnx", False),
        ).run()

        return res

    def run_language_same_guardrail(self, test_data):
        """
        Run a language guardrail using the given test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing the response, and threshold.

        Returns:
        The result of the language guardrail.
        """
        res = LanguageSame(
            prompt=test_data["prompt"],
            response=test_data["response"],
            threshold=test_data["test_arguments"].get("threshold", 0.1),
            transformers_kwargs=test_data["test_arguments"].get(
                "transformers_kwargs", None
            ),
        ).run()

        return res

    def run_nsfw_guardrail(self, test_data):
        """
        Run a nsfw guardrail using the given test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing the prompt, and threshold.

        Returns:
        The result of the nsfw guardrail.
        """
        res = NSFW(
            prompt=test_data["prompt"],
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        ).run()

        return res

    def run_politeness_guardrail(self, test_data):
        """
        Run a politeness guardrail using the given test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing the prompt, and threshold.

        Returns:
        The result of the politeness guardrail.
        """
        res = Politeness(
            prompt=test_data["prompt"],
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        ).run()

        return res

    def run_gibberish_guardrail(self, test_data):
        """
        Run a gibberish guardrail using the given test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing the prompt, and threshold.

        Returns:
        The result of the gibberish guardrail.
        """
        res = Gibberish(
            prompt=test_data["prompt"],
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        ).run()

        return res

    def run_valid_sql_guardrail(self, test_data):
        """
        Run a valid_sql guardrail using the given test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing the prompt.

        Returns:
        The result of the valid_sql guardrail.
        """
        res = ValidSql(
            prompt=test_data["prompt"],
        ).run()

        return res

    def run_valid_csv_guardrail(self, test_data):
        """
        Run a valid_csv guardrail using the given test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing the prompt.

        Returns:
        The result of the valid_csv guardrail.
        """
        res = ValidCsv(
            prompt=test_data["prompt"],
        ).run()

        return res

    def run_malicious_url_guardrail(self, test_data):
        """
        Run a malicious URL guardrail using the given test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing the response, and threshold.

        Returns:
        The result of the malicious URL guardrail.
        """
        res = MaliciousURLs(
            question=test_data["prompt"],
            response=test_data["response"],
            threshold=test_data["test_arguments"].get("threshold", 0.5),
            use_onnx=test_data["test_arguments"].get("use_onnx", False),
        ).run()

        return res

    def run_no_refusal_guardrail(self, test_data):
        """
        Run a no refusal guardrail using the given test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing the response, and threshold.

        Returns:
        The result of the no refusal guardrail.
        """
        res = NoRefusal(
            question=test_data["prompt"],
            response=test_data["response"],
            threshold=test_data["test_arguments"].get("threshold", 0.75),
            match_type=test_data["test_arguments"].get("match_type", "full"),
            use_onnx=test_data["test_arguments"].get("use_onnx", False),
        ).run()

        return res

    def run_reading_time_guardrail(self, test_data):
        """
        Run a reading time guardrail using the given test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing the response, and threshold.

        Returns:
        The result of the reading time guardrail.
        """
        res = ReadingTime(
            question=test_data["prompt"],
            response=test_data["response"],
            threshold=test_data["test_arguments"].get("threshold", 1),
            truncate=test_data["test_arguments"].get("truncate", False),
        ).run()

        return res

    def run_regex_guardrail(self, test_data):
        """
        Run a regex guardrail using the given test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing the response, and threshold.

        Returns:
        The result of the regex guardrail.
        """
        res = Regex(
            prompt=test_data["prompt"],
            patterns=test_data["test_arguments"].get("patterns"),
            is_blocked=test_data["test_arguments"].get("is_blocked", True),
            match_type=test_data["test_arguments"].get("match_type", "search"),
            redact=test_data["test_arguments"].get("redact", True),
        ).run()

        return res

    def run_secrets_guardrail(self, test_data):
        """
        Run a secrets guardrail using the given test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing the response, and threshold.

        Returns:
        The result of the secrets guardrail.
        """
        res = Secrets(
            prompt=test_data["prompt"],
            redact_mode=test_data["test_arguments"].get("redact_mode", "all"),
        ).run()

        return res

    def run_sensitive_guardrail(self, test_data):
        """
        Run a sensitive guardrail using the given test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing the response, and threshold.

        Returns:
        The result of the sensitive guardrail.
        """
        res = Sensitive(
            prompt=test_data["prompt"],
            response=test_data["response"],
            threshold=test_data["test_arguments"].get("threshold", 0.5),
            entity_types=test_data["test_arguments"].get("entity_types", []),
            redact=test_data["test_arguments"].get("redact", True),
            use_onnx=test_data["test_arguments"].get("use_onnx", False),
        ).run()

        return res

    def run_sentiment_guardrail(self, test_data):
        """
        Run a sentiment guardrail using the given test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing the response, and threshold.

        Returns:
        The result of the sentiment guardrail.
        """
        res = Sentiment(
            prompt=test_data["prompt"],
            threshold=test_data["test_arguments"].get("threshold", -0.1),
        ).run()

        return res

    def run_tokenlimit_guardrail(self, test_data):
        """
        Run a tokenlimit guardrail using the given test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing the response, and threshold.

        Returns:
        The result of the tokenlimit guardrail.
        """
        res = TokenLimit(
            question=test_data["prompt"],
            # response=test_data["response"],
            threshold=test_data["test_arguments"].get("threshold", 4096),
        ).run()

        return res

    def run_url_reachability_guardrail(self, test_data):
        """
        Run a url reachability guardrail using the given test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing the response, and threshold.

        Returns:
        The result of the url reachability guardrail.
        """
        res = URLReachability(
            question=test_data["prompt"],
            response=test_data["response"],
            success_status_codes=test_data["test_arguments"].get(
                "success_status_codes", [200, 201, 202, 301, 302]
            ),
            timeout=test_data["test_arguments"].get("timeout", 5),
            threshold=test_data["test_arguments"].get("threshold", 0.5),
        ).run()

        return res

    def run_json_verify_guardrail(self, test_data):
        """
        Run a json test in guardrail using the given test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing the response, and threshold.

        Returns:
        The result of the json test guardrail.
        """
        res = JSONVerify(
            prompt=test_data["prompt"],
            response=test_data["response"],
            repair=test_data["test_arguments"].get("repair", True),
        ).run()

        return res

    def run_valid_python_guardrail(self, test_data):
        """
        Run a python test in guardrail using the given test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing the response, score and is_passed.

        Returns:
            The result of the valid_python test guardrail.
        """
        try:
            prompt = test_data["prompt"]
        except Exception as e:
            prompt = None
        res = ValidPython(
            prompt=prompt,
            response=test_data["response"],
        ).run()

        return res

    def run_profanity_guardrail(self, test_data):
        """
        Run a profanity check in guardrail using the given test data.

        Args:
            self: The object instance
            test_data (dict): A dictionary containing the prompt, response, score and is_passed.

        Returns:
            The result of the valid_python test guardrail.
        """
        try:
            prompt = test_data["prompt"]
        except:
            prompt = None
        res = Profanity(
            question=prompt,
            response=test_data["response"],
            threshold=test_data["test_arguments"].get("threshold", 0.5),
            use_onnx=test_data["test_arguments"].get("use_onnx", False),
        ).run()

        return res

    def run_lmrc_vulnerability_scanner(self, test_data):
        """
        Run LMRC vulnerability scanner function.

        Args:
            self: The instance of the class.
            test_data: The test data for the vulnerability scanner.

        Returns:
            The result of the vulnerability scanner.
        """

        # TODO: add support for multiple probe at a time
        res = lmrc_vulnerability_scanner(
            client=self.client,
            category=test_data["test_arguments"].get("category", "Bullying"),
            prompt=test_data["prompt"],
            response=test_data["response"],
            model=test_data["test_arguments"].get("model", "gpt-3.5-turbo"),
        )
        # TODO: Check if the results are in the desired form
        return res

    def run_dan_vulnerability_scanner(self, test_data):
        """
        Run LMRC vulnerability scanner function.

        Args:
            self: The instance of the class.
            test_data: The test data for the vulnerability scanner.

        Returns:
            The result of the vulnerability scanner.
        """

        # TODO: add support for multiple probe at a time
        res = dan_vulnerability_scanner(
            client=self.client,
            category=test_data["test_arguments"].get("category", "DUDE"),
            prompt=test_data["prompt"],
            response=test_data["response"],
            model=test_data["test_arguments"].get("model", "gpt-3.5-turbo"),
        )
        # TODO: Check if the results are in the desired form
        return res

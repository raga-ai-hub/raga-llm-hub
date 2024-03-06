from raga_llm_hub.metrics.retrieval.f1_at_k import F1ScoreAtK
from raga_llm_hub.metrics.retrieval.f1_score import F1Score
from raga_llm_hub.metrics.retrieval.precision import Precision
from raga_llm_hub.metrics.retrieval.precision_at_k import PrecisionAtK
from raga_llm_hub.metrics.retrieval.recall import Recall
from raga_llm_hub.metrics.retrieval.recall_at_k import RecallAtK

metric_classes = {
    "Precision": Precision,
    "Recall": Recall,
    "F1Score": F1Score,
    "PrecisionAtK": PrecisionAtK,
    "RecallAtK": RecallAtK,
    "F1ScoreAtK": F1ScoreAtK,
}


def context_retrieval_metrics_test(
    expected_context,
    context,
    metric_name,
    threshold=0.6,
    relevance_threshold=0.9,
    k=None,
):
    """
    Test context retrieval metrics including precision, recall, F1 score, and their variations at K.

    Args:
        expected_context (list): List of actual relevant item .
        context (list): List of predicted items.
        metric_name (str): Name of the metric for evaluation ('Precision', 'Recall', 'F1Score', 'PrecisionAtK', 'RecallAtK', 'F1ScoreAtK').
        k (int): The number of top items to consider for 'AtK' metrics.
        threshold (float, optional): Threshold value for determining pass/fail status in evaluations. Defaults to 0.6.
        relevance_threshold(float, optionat): default is set to 0.9

    Returns:
        dict: A dictionary containing the evaluation results.
    """

    # Validate the metric name and ensure required parameters are provided for 'AtK' metrics
    valid_metrics = [
        "Precision",
        "Recall",
        "F1Score",
        "PrecisionAtK",
        "RecallAtK",
        "F1ScoreAtK",
    ]
    if metric_name not in valid_metrics:
        raise ValueError(f"Invalid metric_name. Available metrics: {valid_metrics}")

    if "AtK" in metric_name and k is None:
        raise ValueError("k parameter must be provided for 'AtK' metrics.")

    # Initialize and run the metric
    if "AtK" in metric_name:
        metric_instance = metric_classes[metric_name](
            expected_context, context, threshold, relevance_threshold, k=k
        )
    else:
        metric_instance = metric_classes[metric_name](
            expected_context, context, threshold, relevance_threshold
        )

    score = metric_instance.run()

    # Determine if the calculated score passes the given threshold
    status = True if score >= threshold else False

    # Compile the results into a dictionary to return
    result = {
        "metric_name": metric_name,
        "score": score,
        "threshold": threshold,
        "is_passed": status,
        "evaluated_with": {"k": k, "relevance_threshold": relevance_threshold},
    }

    return result


# if __name__ == "__main__":
#      context=["London, the capital of England and the United Kingdom",
#            "As one of the world's major global cities,[16] London exerts a strong influence on world art, entertainment, fashion, commerce and finance, education, health care, media, science and technology, tourism, transport, and communications",
#            "The French Revolution was a period of political and societal change in France that began with the Estates General of 1789, and ended with the coup of 18 Brumaire in November 1799 and the formation of the French Consulate"]


#      expected_context=["London, the capital of England and the United Kingdom",
#                      "The City of London, its ancient core and financial centre, was founded by the Romans as Londinium and retains its medieval boundaries",
#                      "As one of the world's major global cities,[16] London exerts a strong influence on world art, entertainment, fashion, commerce and finance, education, health care, media, science and technology, tourism, transport, and communications",
#                       "The 2023 population of Greater London of just under 10 million[27] made it Europe's third-most populous city" ]
#      result = context_retrieval_metrics_test(expected_context, context, metric_name="Precision", k= 2,  )
#      print(result)

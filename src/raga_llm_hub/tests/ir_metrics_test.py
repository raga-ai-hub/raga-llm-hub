import json

from ..metrics.retrieval import *


def ir_metrics_test(
    client,
    prompt,
    retrieved_context,
    metric_name,
    rel,
    cutoff,
    min_rel,
    max_rel,
    p,
    normalize,
    T,
    recall,
    alpha,
    judged_only,
    dcg,
    gains,
    beta,
    relative,
    model,
    threshold,
):
    """
    Initializes the class instance with the provided parameters.

    Args:
        client: An instance of the client used for relevancy
        prompt: a prompt string used for ir test
        retrieved_context: list of contexts, reference for the prompt
        metric_name: Name of the metric for evaluation (e.g., 'nDCG', 'Precision').
        rel: Relevance threshold to distinguish relevant from non-relevant documents.
        cutoff: Ranking position at which evaluation is truncated.
        min_rel: Minimum relevance score that can be assigned to a document.
        max_rel: Maximum relevance score that can be assigned to a document.
        p: Persistence parameter used in metrics like Rank-Biased Precision.
        normalize: Boolean indicating if the metric score should be normalized.
        T: Total desired gain or threshold for some metrics.
        recall: Recall level for precision at recall calculations.
        alpha: Redundancy intolerance parameter in diversity metrics.
        judged_only: Boolean to consider only documents that have been judged.
        dcg: Specifies the DCG formulation to use in nDCG calculations.
        gains: Custom gain mapping for non-standard relevance-to-gain mappings.
        beta: Specifies relative importance of recall to precision in F-score.
        relative: Boolean for calculating precision relative to maximum possible SetP.
        threshold: Threshold value for determining pass/fail status in evaluations.

    Returns:
        dict: A dictionary containing the evaluation results.

    """

    # List of all supported measures. This list should be updated as new measures are implemented.
    all_measures = [
        "Accuracy",
        "AP",
        "BPM",
        "Bpref",
        "Compat",
        "infAP",
        "INSQ",
        "INST",
        "IPrec",
        "Judged",
        "nDCG",
        "NERR10",
        "NERR11",
        "NERR8",
        "NERR9",
        "NumQ",
        "NumRel",
        "NumRet",
        "P",
        "R",
        "Rprec",
        "SDCG",
        "SetAP",
        "SetF",
        "SetP",
        "SetR",
        "Success",
    ]

    # Check if the specified metric name is among the supported measures.
    if metric_name != "all" and metric_name not in all_measures:
        raise ValueError("Invalid metric_name. Available metric_name: ", all_measures)
    rm = retrieval_metrics.RetrievalMetrics()
    query_relevance, runs = rm.get_qrel_run(
        client=client,
        prompt=prompt,
        model=model,
        retrieved_context=retrieved_context,
        threshold=0.3,
    )

    if metric_name == "all":
        score, status = {}, {}
        for measure in all_measures:
            measure_instance = globals()[measure](
                qrels=query_relevance,
                runs=runs,
                rel=rel,
                cutoff=cutoff,
                min_rel=min_rel,
                max_rel=max_rel,
                p=p,
                normalize=normalize,
                T=T,
                recall=recall,
                alpha=alpha,
                judged_only=judged_only,
                dcg=dcg,
                gains=gains,
                beta=beta,
                relative=relative,
            )
            score[measure] = measure_instance.run()
            status[measure] = "True" if score[measure] > threshold else "False"
    else:
        # Dynamically create an instance of the specified metric with provided parameters.
        measure_instance = globals()[metric_name](
            qrels=query_relevance,
            runs=runs,
            rel=rel,
            cutoff=cutoff,
            min_rel=min_rel,
            max_rel=max_rel,
            p=p,
            normalize=normalize,
            T=T,
            recall=recall,
            alpha=alpha,
            judged_only=judged_only,
            dcg=dcg,
            gains=gains,
            beta=beta,
            relative=relative,
        )

        # Calculate the score using the instantiated metric.
        score = measure_instance.run()

        # Determine if the calculated score passes the given threshold.
        status = True if score > threshold else False

    reason = f"\n\nGroundTruth Query-Document Mapping: {json.dumps(query_relevance)} \n\n Retrived Query-Document Mapping: {json.dumps(runs)} \n\n Note: 'Q' denotes Query(prompt) and 'D' denotes Document(context)"

    # Compile the results into a dictionary to return.
    result = {
        "prompt": prompt,
        "context": retrieved_context,
        "score": score,
        "is_passed": status,
        "evaluated_with": {
            "model": model,
            "include_reason": reason,
        },
    }

    return result

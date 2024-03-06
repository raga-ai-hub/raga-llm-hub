import math

from ...tests.contextual_relevancy_test import ContextualRelevancyTest
from ..base_metrics import Metrics


def normal_round(n):
    if n - math.floor(n) < 0.5:
        return math.floor(n)
    return math.ceil(n)


class RetrievalMetrics(Metrics):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_qrel_run(
        self,
        client,
        prompt,
        retrieved_context,
        model="gpt-3.5-turbo",
        include_reason=False,
        threshold=0.5,
    ):
        qrels = {"Q0": {}}
        runs = {"Q0": {}}

        for idx, context in enumerate(retrieved_context):
            res = ContextualRelevancyTest(
                client=client,
                question=prompt,
                retrieval_context=context,
                model=model,
                include_reason=include_reason,
                threshold=threshold,
            ).run()
            d_key = "D" + str(idx)
            qrels["Q0"][d_key] = normal_round(res["score"])
            runs["Q0"][d_key] = res["score"]

        return qrels, runs

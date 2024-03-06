import ir_measures as ir

from .retrieval_metrics import RetrievalMetrics


def filter_kwargs(kwargs):
    return {k: v for k, v in kwargs.items() if v is not None}


class Rprec:
    def __init__(self, qrels, runs, **kwargs):
        super().__init__()
        self.rel = kwargs.get("rel", None)
        self.judged_only = kwargs.get("judged_only", None)
        self.qrels = qrels
        self.runs = runs

    def run(self):
        filtered_kwargs = filter_kwargs(
            {"rel": self.rel, "judged_only": self.judged_only}
        )
        measure = ir.Rprec(**filtered_kwargs)
        result = ir.calc_aggregate([measure], self.qrels, self.runs)
        return result[measure]

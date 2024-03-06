import ir_measures as ir

from .retrieval_metrics import RetrievalMetrics


def filter_kwargs(kwargs):
    return {k: v for k, v in kwargs.items() if v is not None}


class RBP:
    def __init__(self, qrels, runs, **kwargs):
        super().__init__()
        self.cutoff = kwargs.get("cutoff", None)
        self.p = kwargs.get("p", None)
        self.rel = kwargs.get("rel", None)
        self.qrels = qrels
        self.runs = runs

    def run(self):
        filtered_kwargs = filter_kwargs(
            {"cutoff": self.cutoff, "p": self.p, "rel": self.rel}
        )
        measure = ir.RBP(**filtered_kwargs)
        result = ir.calc_aggregate([measure], self.qrels, self.runs)
        return result[measure]

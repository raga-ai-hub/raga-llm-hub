import ir_measures as ir

from .retrieval_metrics import RetrievalMetrics


def filter_kwargs(kwargs):
    return {k: v for k, v in kwargs.items() if v is not None}


class NumRel:
    def __init__(self, qrels, runs, **kwargs):
        super().__init__()
        self.rel = kwargs.get("rel", 1)
        self.qrels = qrels
        self.runs = runs
        if self.rel != 1:
            raise ValueError("rel=1 is required for numrel")

    def run(self):
        filtered_kwargs = filter_kwargs({"rel": self.rel})
        measure = ir.NumRel(**filtered_kwargs)
        result = ir.calc_aggregate([measure], self.qrels, self.runs)
        return result[measure]

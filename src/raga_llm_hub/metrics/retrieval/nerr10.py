import ir_measures as ir

from .retrieval_metrics import RetrievalMetrics


def filter_kwargs(kwargs):
    return {k: v for k, v in kwargs.items() if v is not None}


class NERR10:
    def __init__(self, qrels, runs, **kwargs):
        super().__init__()
        self.p = kwargs.get("p", None)
        self.min_rel = kwargs.get("min_rel", None)
        self.max_rel = kwargs.get("max_rel", None)
        self.qrels = qrels
        self.runs = runs
        if self.max_rel == None:
            raise ValueError("max_rel is required for nerr10")

    def run(self):
        filtered_kwargs = filter_kwargs(
            {"p": self.p, "min_rel": self.min_rel, "max_rel": self.max_rel}
        )
        measure = ir.NERR10(**filtered_kwargs)
        result = ir.calc_aggregate([measure], self.qrels, self.runs)
        return result[measure]

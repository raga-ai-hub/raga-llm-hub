import ir_measures as ir

from .retrieval_metrics import RetrievalMetrics


def filter_kwargs(kwargs):
    return {k: v for k, v in kwargs.items() if v is not None}


class Compat:
    def __init__(self, qrels, runs, **kwargs):
        super().__init__()
        self.p = kwargs.get("p", None)
        self.normalize = kwargs.get("normalize", None)
        self.qrels = qrels
        self.runs = runs

    def run(self):
        filtered_kwargs = filter_kwargs({"p": self.p, "normalize": self.normalize})
        measure = ir.Compat(**filtered_kwargs)
        result = ir.calc_aggregate([measure], self.qrels, self.runs)
        return result[measure]

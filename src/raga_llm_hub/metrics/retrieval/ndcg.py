import ir_measures as ir

from .retrieval_metrics import RetrievalMetrics


def filter_kwargs(kwargs):
    return {k: v for k, v in kwargs.items() if v is not None}


class nDCG:
    def __init__(self, qrels, runs, **kwargs):
        super().__init__()
        self.cutoff = kwargs.get("cutoff", None)
        self.dcg = kwargs.get("dcg", None)
        self.gains = kwargs.get("gains", None)
        self.judged_only = kwargs.get("judged_only", None)
        self.qrels = qrels
        self.runs = runs
        if self.cutoff == None:
            raise ValueError("cutoff is required for nDCG")

    def run(self):
        filtered_kwargs = filter_kwargs(
            {
                "cutoff": self.cutoff,
                "dcg": self.dcg,
                "gains": self.gains,
                "judged_only": self.judged_only,
            }
        )
        measure = ir.nDCG(**filtered_kwargs)
        result = ir.calc_aggregate([measure], self.qrels, self.runs)
        return result[measure]

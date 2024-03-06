# from numpy import nan
import math

import ir_measures as ir

from .retrieval_metrics import RetrievalMetrics


def filter_kwargs(kwargs):
    return {k: v for k, v in kwargs.items() if v is not None}


class Accuracy:
    def __init__(self, qrels, runs, **kwargs):
        super().__init__()
        self.cutoff = kwargs.get("cutoff", None)
        self.rel = kwargs.get("rel", None)
        self.qrels = qrels
        self.runs = runs

    def run(self):
        filtered_kwargs = filter_kwargs({"cutoff": self.cutoff, "rel": self.rel})
        measure = ir.Accuracy(**filtered_kwargs)
        result = ir.calc_aggregate([measure], self.qrels, self.runs)
        if math.isnan(result[measure]):
            result[measure] = 0
        return result[measure]

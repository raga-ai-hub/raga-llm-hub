from ir_metrics.retrieval import *


def run_measures_test(threshold):
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

    qrels = {"Q0": {"D0": 0, "D1": 1}, "Q1": {"D0": 0, "D3": 2}}
    runs = {"Q0": {"D0": 1.2, "D1": 1.0}, "Q1": {"D0": 2.4, "D3": 3.6}}

    for measure in all_measures:
        m = globals()[measure](
            qrels=qrels,
            runs=runs,
            rel=1,
            cutoff=2,
            min_rel=0,
            max_rel=2,
            p=0.2,
            normalize=False,
            T=0.1,
            recall=0.5,
            judged_only=True,
        )
        score = m.run()
        status = True if score > threshold else False
        print(measure, "\t  :", status, "Score: ", score)


run_measures_test(0.2)

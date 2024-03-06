from .retrieval import *


def run_measures_test(threshold):
    # Define a dictionary mapping measure names to their corresponding classes
    all_measures = {
        "Accuracy": Accuracy,
        "AP": AP,
        "BPM": BPM,
        "Bpref": Bpref,
        "Compat": Compat,
        "infAP": infAP,
        "INSQ": INSQ,
        "INST": INST,
        "IPrec": IPrec,
        "Judged": Judged,
        "nDCG": nDCG,
        "NERR10": NERR10,
        "NERR11": NERR11,
        "NERR8": NERR8,
        "NERR9": NERR9,
        "NumQ": NumQ,
        "NumRel": NumRel,
        "NumRet": NumRet,
        "P": P,
        "R": R,
        "Rprec": Rprec,
        "SDCG": SDCG,
        "SetAP": SetAP,
        "SetF": SetF,
        "SetP": SetP,
        "SetR": SetR,
        "Success": Success,
    }

    qrels = {"Q0": {"D0": 0, "D1": 1}, "Q1": {"D0": 0, "D3": 2}}
    runs = {"Q0": {"D0": 1.2, "D1": 1.0}, "Q1": {"D0": 2.4, "D3": 3.6}}

    for measure_name, measure_class in all_measures.items():
        if measure_class is None:
            print(f"{measure_name} is not imported.")
            continue
        m = measure_class(
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
        print(f"{measure_name}: {status} Score: {score}")


run_measures_test(0.2)

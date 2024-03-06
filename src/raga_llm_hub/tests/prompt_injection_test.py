import torch
from transformers import (AutoModelForSequenceClassification, AutoTokenizer,
                          pipeline)


def prompt_injection_test(prompt, threshold=0.5):
    tokenizer = AutoTokenizer.from_pretrained(
        "ProtectAI/deberta-v3-base-prompt-injection"
    )
    model = AutoModelForSequenceClassification.from_pretrained(
        "ProtectAI/deberta-v3-base-prompt-injection"
    )

    classifier = pipeline(
        "text-classification",
        model=model,
        tokenizer=tokenizer,
        truncation=True,
        max_length=512,
        device=torch.device("cuda" if torch.cuda.is_available() else "cpu"),
    )

    if classifier(prompt)[0]["label"] == "INJECTION":
        is_non_breakable = False
        injection_score = classifier(prompt)[0]["score"]
    else:
        is_non_breakable = True
        injection_score = 1 - classifier(prompt)[0]["score"]

    result = {
        "prompt": prompt,
        "threshold": threshold,
        "is_passed": is_non_breakable,
        "score": injection_score,
    }

    return result

class CorrectnessTemplate:
    @staticmethod
    def generate_correctness_prompt(question, answer, expected_response, context):
        return f"""Given the input with question, answer, expected_response, context and based on the instruction below create JSON similar to the examples for the input with keys `question`, `answer`, `expected_response`, `extracted_statements`:
    Input:
    {{{{"question":
    {question}
    "answer":
    {answer}
    "expected_response":
    {expected_response}
    "context":
    {context}
    }}}}


    Instruction:
    Extract following from input question, ground truth based on the context
    "extraced_statements":
        "TP": statements that are present in both the answer and the ground truth,
        "FP": statements present in the answer but not found in the ground truth,
        "FN": relevant statements found in the ground truth but omitted in the answer,


    Example:
    {{
        "question": "What powers the sun and what is its primary function?",
        "answer": "The sun is powered by nuclear fission, similar to nuclear reactors on Earth, and its primary function is to provide light to the solar system.",
        "ground_truth": "The sun is actually powered by nuclear fusion, not fission. In its core, hydrogen atoms fuse to form helium, releasing a tremendous amount of energy. This energy is what lights up the sun and provides heat and light, essential for life on Earth. The sun's light also plays a critical role in Earth's climate system and helps to drive the weather and ocean currents.",
        "extracted_statements": {{
            "TP": ["The sun's primary function is to provide light"],
            "FP": [
                "The sun is powered by nuclear fission",
                "similar to nuclear reactors on Earth",
            ],
            "FN": [
                "The sun is powered by nuclear fusion, not fission",
                "In its core, hydrogen atoms fuse to form helium, releasing a tremendous amount of energy",
                "This energy provides heat and light, essential for life on Earth",
                "The sun's light plays a critical role in Earth's climate system",
                "The sun helps to drive the weather and ocean currents",
            ],
        }},
    }},
    {{
        "question": "What is the boiling point of water?",
        "answer": "The boiling point of water is 100 degrees Celsius at sea level.",
        "ground_truth": "The boiling point of water is 100 degrees Celsius (212 degrees Fahrenheit) at sea level, but it can change with altitude.",
        "extracted_statements": {{
            "TP": [
                "The boiling point of water is 100 degrees Celsius at sea level"
            ],
            "FP": [],
            "FN": [
                "The boiling point can change with altitude",
                "The boiling point of water is 212 degrees Fahrenheit at sea level",
            ],
        }},
    }}
    ===== END OF EXAMPLE ======
    The key extracted_statements in the JSON should stricly have multiple sentences separated by comma if any.
    """


class CoherenceTemplate:
    @staticmethod
    def generate_verdict(prompt, response):
        return f"""Given a input and submission. Evaluate the submission only using the given criteria. Use only 'Yes' (1) and 'No' (0) as verdict.

        Example:
        {{
            "input": "Who was the director of Los Alamos Laboratory?",
            "submission": "Einstein was the director of  Los Alamos Laboratory.",
            "criteria": "Is the output written in perfect grammar",
            "output": {{
                "reason": "the criteria for evaluation is whether the output is written in perfect grammar. In this case, the output is grammatically correct.",
                "verdict": "1"
            }}
        }}
        {{
            "input": "What is the capital of France?",
            "submission": "capital is paris",
            "criteria": "Does the submission presents ideas, information, or arguments in a logical and organized manner?",
            "output": {{
                "reason": "The criteria for evaluation is whether the output is coherent with the context. In this case, the output is not coherent with the context.",
                "verdict": "0"
            }}
        }}
        ===== END OF EXAMPLE =====
        Input:
        {{
        {prompt}

        Submission:
        {response}

        Criteria:"Does the submission presents ideas, information, or arguments in a logical and organized manner?"
        }}


        JSON:
        """


class ConcisenessTemplate:
    @staticmethod
    def generate_verdict(prompt, response):
        return f"""Given a input and submission. Evaluate the submission only using the given criteria and return JSON with the input, submission and verdict. Use only 'Yes' (1) and 'No' (0) as verdict.

    Example:
    {{
        "input": "Who was the director of Los Alamos Laboratory?",
        "submission": "Einstein was the director of  Los Alamos Laboratory.",
        "criteria": "Is the output written in perfect grammar",
        "output": {{
            "reason": "the criteria for evaluation is whether the output is written in perfect grammar. In this case, the output is grammatically correct.",
            "verdict": "1"
        }}
    }}

    Given:

    "input":
    {prompt}

    "submission":
    {response}

    "criteria":"Does the submission conveys information or ideas clearly and efficiently, without unnecessary or redundant details?"

    "output":

    Return JSON with the input as {prompt} and submission as {response}:
    """

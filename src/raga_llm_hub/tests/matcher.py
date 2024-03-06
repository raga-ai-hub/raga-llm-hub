# matching_module.py

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class Matcher:
    def __init__(self, substrings, matchtype="str", threshold=0.5):
        self.substrings = substrings
        self.matchtype = matchtype
        self.threshold = threshold

        # Vectorize the substrings
        self.vectorizer = TfidfVectorizer(preprocessor=self.preprocess_string)
        self.substrings_vectorized = self.vectorizer.fit_transform(substrings)

    def preprocess_string(self, string):
        return string.lower()

    def match(self, response):
        result = []
        for output in response:
            output = self.preprocess_string(output)
            output_vectorized = self.vectorizer.transform([output])

            match = False
            if self.matchtype == "str":
                similarities = cosine_similarity(
                    output_vectorized, self.substrings_vectorized
                )
                max_similarity = np.max(similarities)
                if max_similarity >= self.threshold:
                    match = True

            elif self.matchtype == "word":
                words = output.split()
                for word in words:
                    word_vectorized = self.vectorizer.transform([word])
                    similarities = cosine_similarity(
                        word_vectorized, self.substrings_vectorized
                    )
                    max_similarity = np.max(similarities)
                    if max_similarity >= self.threshold:
                        match = True
                        break

            result.append(match)
        return result

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer


class Sentiment:
    """
    A sentiment scanner based on the NLTK's SentimentIntensityAnalyzer. It is used to detect if a prompt
    has a sentiment score lower than the threshold, indicating a negative sentiment.
    """

    def __init__(self, prompt: str, threshold: float = -0.1):
        """
        Initializes Sentiment with a threshold and a chosen lexicon.

        Parameters:
            prompt (str): The prompt to scan for sentiment.
           threshold (float): Threshold for the sentiment score (from -1 to 1). Default is -0.1.

        Raises:
           None.
        """

        nltk.download("vader_lexicon")
        self.response = prompt
        self._sentiment_analyzer = SentimentIntensityAnalyzer()
        self._threshold = threshold

    def run(self) -> (str, bool, float):  # type: ignore
        result = {
            "response": self.response,
            "is_passed": False,
            "score": 0.0,
        }

        sentiment_score = self._sentiment_analyzer.polarity_scores(self.response)

        sentiment_score_compound = sentiment_score["compound"]

        print("sentiment_score_compound", sentiment_score_compound)
        print("threshold", self._threshold)

        if sentiment_score_compound < -0.05:
            if sentiment_score_compound < self._threshold:
                result["reason"] = "Sentiment is negative and score is below threshold."
                result["is_passed"] = False
                result["score"] = sentiment_score_compound
                return result
            elif sentiment_score_compound > self._threshold:
                result["reason"] = "Sentiment is negative and score is above threshold."
                result["is_passed"] = True
                result["score"] = sentiment_score_compound
                return result
        elif sentiment_score_compound > 0.05:
            if sentiment_score_compound > self._threshold:
                result["reason"] = "Sentiment is positive and score is above threshold."
                result["is_passed"] = True
                result["score"] = sentiment_score_compound
                return result
            elif sentiment_score_compound < self._threshold:
                result["reason"] = "Sentiment is positive and score is below threshold."
                result["is_passed"] = False
                result["score"] = sentiment_score_compound
                return result
        else:
            result["reason"] = "Sentiment is neutral."
            result["is_passed"] = True
            result["score"] = sentiment_score_compound
            return result

        return result

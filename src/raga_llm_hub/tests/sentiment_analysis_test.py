"""
Detect Sentiment of the response. This test can be used to regulate the sentiment of the response from the model
depending on the requiremnts of the downstream application
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def sentiment_analysis_test(response, threshold=0.5):
    """
    Provides a score for the sentiment of model response. The test can be used to regulate
    the sentiment of the model to keep it based on the application requirement.
    It return overall text sentiment higher score is positive sentiment

    Args:
    - response (str): The response from the model.
    - threshold (float): The threshold to define the sentiment

    Returns:
    - dict: A dictionary containing the response, sentimentscore, threshold and
    boolean if sentiment score is more than threshold

    """

    # Create a test case
    analyzer = SentimentIntensityAnalyzer()

    sentiment_score = analyzer.polarity_scores(response)

    score = (
        sentiment_score["compound"] + 1
    ) / 2  # changing range from -1 to 1 to 0 to 1
    is_positive_sentiment = True if sentiment_score["compound"] > threshold else False

    # Prepare and return the result
    result = {
        "response": response,
        "threshold": threshold,
        "is_passed": is_positive_sentiment,
        "score": score,
    }

    return result

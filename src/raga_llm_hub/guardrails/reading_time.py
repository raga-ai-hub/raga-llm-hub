class ReadingTime:
    """
    Scanner that checks the reading time of the output against a maximum time.

    If the output exceeds the maximum time, the output will be truncated to fit within the time limit.
    """

    def __init__(self, question, response, threshold=1, truncate=False):
        """
        Args:
        - question: str, the question to be evaluated for contextual relevancy
        - response: str, the response for the question
        - max_time: Maximum time in minutes that the user should spend reading the output.
        - truncate: If True, the output will be truncated to the maximum time.
        """

        self.question = question
        self.output = response

        self._max_time = threshold
        self._truncate = truncate
        self._words_per_minute = 200  # Average reading speed

    def run(self):
        words = self.output.split()
        word_count = len(words)
        reading_time_minutes = word_count / self._words_per_minute

        if self._truncate:
            # Calculate the maximum number of words to fit within the time limit
            max_words = int(self._max_time * self._words_per_minute)
            trunc_output = " ".join(words[:max_words])

        result = {
            "prompt": self.question,
            "response": self.output,
            "score": reading_time_minutes,
            "threshold": self._max_time,
            "is_passed": (True if reading_time_minutes < self._max_time else False),
            "truncated_output": trunc_output if self._truncate else self.output,
        }
        return result

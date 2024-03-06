class LatencyTest:
    def __init__(self, latency, threshold=10.0):
        """
        Initialize the LatencyTest class with the given latency and threshold.

        Parameters:
            latency (float): The latency value for the test.
            threshold (float, optional): The threshold for the test. Defaults to 10.0.
        """
        self.latency = latency
        self.threshold = threshold

    def run(self):
        """
        Run the latency test and return a dictionary containing the score, threshold, and a boolean indicating if the test passed.
        """
        success = self.latency <= self.threshold
        test_result = {
            "score": self.latency,
            "threshold": self.threshold,
            "is_passed": success,
        }
        return test_result


# # Example usage:
# if __name__ == "__main__":
#     test_instance = LatencyTest(latency=9.9)
#     result = test_instance.run()
#     print(result)

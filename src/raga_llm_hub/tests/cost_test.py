class CostTest:
    def __init__(self, cost, threshold=0.4):
        """
        Initialize the CostTest class with the given cost and threshold.

        Parameters:
            cost (float): The cost value for the test.
            threshold (float, optional): The threshold for the test. Defaults to 0.4.
        """
        self.cost = cost
        self.threshold = threshold

    def run(self):
        """
        Run the cost test and return a dictionary containing the score, threshold, and a boolean indicating if the test passed.
        """
        success = self.cost <= self.threshold
        test_result = {
            "score": self.cost,
            "threshold": self.threshold,
            "is_passed": success,
        }
        return test_result


# # Example usage:
# if __name__ == "__main__":
#     test_instance = CostTest(cost=0.34)
#     result = test_instance.run()
#     print(result)

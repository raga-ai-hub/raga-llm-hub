class Metrics:
    def __init__(self, **kwargs):
        pass

    def run_one(self, *args, **kwargs):
        raise NotImplementedError("This method should be implemented by subclasses.")

    def run(self, *args, **kwargs):
        raise NotImplementedError("This method should be implemented by subclasses.")

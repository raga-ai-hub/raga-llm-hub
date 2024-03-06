from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from .retrieval_metrics import RetrievalMetrics


class Recall(RetrievalMetrics):
    def __init__(self, expected_context, context, threshold):
        super().__init__()
        self.context = context
        self.expected_context = expected_context
        self.threshold = threshold
        self.model = SentenceTransformer("infgrad/stella-base-en-v2")

    def generate_embedding(self, text):
        embeddings = self.model.encode(text, normalize_embeddings=True)
        return embeddings

    def calculate_recall(self, context, expected_context, cos_similarity, threshold):
        relevant_context = []
        for i, row in enumerate(cos_similarity):
            if max(row) >= threshold:
                relevant_context.append(context[i])
        true_positives = len(set(relevant_context) & set(expected_context))
        false_negatives = len(set(expected_context) - set(relevant_context))
        recall = (
            true_positives / (true_positives + false_negatives)
            if (true_positives + false_negatives) != 0
            else 0
        )
        return recall

    def run(self):
        embeddings1 = self.generate_embedding(self.context)
        embeddings2 = self.generate_embedding(self.expected_context)
        cos_similarity = cosine_similarity(embeddings1, embeddings2)
        recall = self.calculate_recall(
            self.context, self.expected_context, cos_similarity, self.threshold
        )
        return recall

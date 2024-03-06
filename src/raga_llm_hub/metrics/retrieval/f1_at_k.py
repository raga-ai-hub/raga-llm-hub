from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from .retrieval_metrics import RetrievalMetrics


class F1ScoreAtK(RetrievalMetrics):
    def __init__(self, expected_context, context, threshold):
        super().__init__()
        self.context = context
        self.expected_context = expected_context
        self.threshold = threshold
        self.model = SentenceTransformer("infgrad/stella-base-en-v2")

    def generate_embedding(self, text):
        embeddings = self.model.encode(text, normalize_embeddings=True)
        return embeddings

    def calculate_f1_score_at_k(
        self, context, expected_context, cos_similarity, threshold, k
    ):
        relevant_context = []
        for i, row in enumerate(cos_similarity):
            if max(row) >= threshold:
                relevant_context.append(context[i])
        relevant_context_at_k = relevant_context[:k]
        true_positives = len(set(relevant_context_at_k) & set(expected_context))
        total_items_at_k = len(relevant_context_at_k)

        precision_at_k = (
            true_positives / total_items_at_k if total_items_at_k != 0 else 0
        )
        total_relevant_items = len(set(expected_context))
        recall_at_k = (
            true_positives / total_relevant_items if total_relevant_items != 0 else 0
        )

        f1_score_at_k = (
            2 * (precision_at_k * recall_at_k) / (precision_at_k + recall_at_k)
            if (precision_at_k + recall_at_k) != 0
            else 0
        )
        return f1_score_at_k

    def run(self, k):
        embeddings1 = self.generate_embedding(self.context)
        embeddings2 = self.generate_embedding(self.expected_context)
        cos_similarity = cosine_similarity(embeddings1, embeddings2)
        f1_score_at_k = self.calculate_f1_score_at_k(
            self.context, self.expected_context, cos_similarity, self.threshold, k
        )
        return f1_score_at_k

from domain.entities import Feedback
from domain.enums import FeedbackResult
from storage.db import feedback_stats_for_symptoms, feedback_stats_for_symptoms_and_disease


class LearningService:
    """Very simple feedback-based learning layer."""

    def trust_for_case(self, symptoms: str) -> float:
        accepted, rejected = feedback_stats_for_symptoms(symptoms)
        total = accepted + rejected
        if total == 0:
            return 0.5  # neutral start

        # accepted ratio, clipped so it never becomes 0 or 1 exactly
        trust = accepted / total
        return max(0.1, min(0.9, trust))

    def is_disease_rejected_for_symptoms(
        self,
        symptoms: str,
        disease: str,
        min_rejections: int = 2
    ) -> bool:
        accepted, rejected = feedback_stats_for_symptoms_and_disease(symptoms, disease)
        return rejected >= min_rejections and rejected > accepted

    # Optional: used by retrain runner in your agent loop
    def reset(self):
        # Here we don't keep in-memory stats; DB is the source of truth.
        pass

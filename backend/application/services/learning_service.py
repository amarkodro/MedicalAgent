from domain.entities import Feedback
from domain.enums import FeedbackResult
from storage.db import feedback_stats_for_symptoms, feedback_stats_for_symptoms_and_disease


class LearningService:
    """Very simple feedback-based learning layer."""

    def trust_for_case(self, symptoms: str) -> float:
        accepted, rejected = feedback_stats_for_symptoms(symptoms)
        total = accepted + rejected

        if total == 0:
            return 0.65

        ratio = accepted / total

        trust = 0.55 + 0.20 * ratio
        return trust

    def is_disease_rejected_for_symptoms(
        self,
        symptoms: str,
        disease: str,
        min_rejections: int = 2
    ) -> bool:
        accepted, rejected = feedback_stats_for_symptoms_and_disease(symptoms, disease)
        return rejected >= min_rejections and rejected > accepted

    def reset(self):
        pass

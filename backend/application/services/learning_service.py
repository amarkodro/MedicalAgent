from domain.entities import Feedback
from domain.enums import FeedbackResult
from datetime import datetime, timezone
from storage.db import feedback_stats_for_symptoms






class LearningService:
    """
    Uči iz povratne informacije (feedback).
    """
    def trust_for_case(self, symptoms: str) -> float:
        accepted, rejected = feedback_stats_for_symptoms(symptoms)
        total = accepted + rejected

        if total == 0:
            return 0.5  # neutralni trust

        return accepted / total

    def __init__(self):
        self.accepted = 0
        self.rejected = 0

    def register_feedback(self, feedback: Feedback):
        if feedback.result == FeedbackResult.ACCEPTED:
            self.accepted += 1
        else:
            self.rejected += 1

    def rejection_rate(self) -> float:
        total = self.accepted + self.rejected
        if total == 0:
            return 0.0
        return self.rejected / total


    def add_feedback(
        self,
        case_id: int,
        prediction_id: int,
        accepted: bool
    ):
        result = (
            FeedbackResult.ACCEPTED
            if accepted
            else FeedbackResult.REJECTED
        )

        feedback = Feedback(
            case_id=case_id,
            prediction_id=prediction_id,
            result=result,
            created_at=datetime.now(timezone.utc)
        )

        self.register_feedback(feedback)

    def load_from_db(self, accepted: int, rejected: int):
        self.accepted = accepted
        self.rejected = rejected    

    def reset(self):
        self.accepted = 0
        self.rejected = 0

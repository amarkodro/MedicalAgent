from application.services.learning_service import LearningService
from storage.db import count_feedback


class RetrainAgentRunner:
    """Decides when retraining is required based on rejection rate."""

    def __init__(self, learning_service: LearningService, rejection_threshold: float = 0.3):
        self.learning_service = learning_service
        self.rejection_threshold = rejection_threshold
        self._retrain_triggered = False

    def reset(self):
        self._retrain_triggered = False

    def tick(self) -> bool:
        accepted, rejected = count_feedback()
        total = accepted + rejected
        rejection_rate = (rejected / total) if total > 0 else 0.0

        if rejection_rate >= self.rejection_threshold and not self._retrain_triggered:
            self._retrain_triggered = True
            return True
        return False

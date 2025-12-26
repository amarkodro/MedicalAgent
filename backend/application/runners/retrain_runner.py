from application.services.learning_service import LearningService
from storage.db import count_feedback


class RetrainAgentRunner:
    """
    Runner koji implementira LEARN fazu agenta.
    Odlučuje DA LI treba retrenirati model.
    """

    def reset(self):
        self._retrain_triggered = False
        
    def __init__(
        self,
        learning_service: LearningService,
        rejection_threshold: float = 0.3
    ):
        self.learning_service = learning_service
        self.rejection_threshold = rejection_threshold
        self._retrain_triggered = False

    def tick(self) -> bool:
    # -------- SENSE --------
        accepted, rejected = count_feedback()
        self.learning_service.load_from_db(accepted, rejected)

    # -------- THINK --------
        rejection_rate = self.learning_service.rejection_rate()

    # -------- ACT --------
        if rejection_rate >= self.rejection_threshold and not self._retrain_triggered:
            self._retrain_triggered = True
            return True

        return False

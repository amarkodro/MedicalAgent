from typing import Optional, List

from domain.entities import Prediction
from application.services.scoring_service import ScoringService
from application.services.db_queue_service import DbQueueService


class ScoringAgentRunner:
    """
    Agent runner:
    Sense -> Think -> Act
    """

    def __init__(self, queue_service: DbQueueService, scoring_service: ScoringService):
        self.queue_service = queue_service
        self.scoring_service = scoring_service

    def tick(self) -> Optional[Prediction]:
        # -------- SENSE --------
        case = self.queue_service.dequeue_next()
        if case is None:
            return None

        # -------- THINK --------
        predictions: List[Prediction] = self.scoring_service.score_top_k(case, k=5)
        if not predictions:
            # fallback
            predictions = [self.scoring_service.score(case)]

        main_prediction = predictions[0]

        # -------- ACT --------
        self.queue_service.update_status(
            case_id=case.id,
            disease=main_prediction.predicted_disease,
            confidence=main_prediction.confidence,
            decision=main_prediction.decision.name,
            predictions=[
                {
                    "disease": p.predicted_disease,
                    "confidence": p.confidence,
                    "decision": p.decision.name,
                }
                for p in predictions
            ],
        )

        return main_prediction

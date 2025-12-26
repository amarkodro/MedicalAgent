from typing import Optional

from domain.entities import MedicalCase, Prediction
from domain.enums import CaseStatus, Decision
from application.services.scoring_service import ScoringService
from application.services.db_queue_service import DbQueueService



class ScoringAgentRunner:
    """
    Agentički runner:
    Sense → Think → Act
    (DB-backed)
    """

    def __init__(
        self,
        queue_service: DbQueueService,
        scoring_service: ScoringService
    ):
        self.queue_service = queue_service
        self.scoring_service = scoring_service

    def tick(self) -> Optional[Prediction]:
        # -------- SENSE --------
        case = self.queue_service.dequeue_next()
        if case is None:
            return None

        # -------- THINK --------
        prediction = self.scoring_service.score(case)

        # -------- ACT --------
        self.queue_service.update_status(
            case_id=case.id,
            disease=prediction.predicted_disease,
            confidence=prediction.confidence,
            decision=prediction.decision.name
        )   
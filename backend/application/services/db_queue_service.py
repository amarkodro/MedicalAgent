from typing import Optional, List, Dict
from datetime import datetime, timezone

from domain.entities import MedicalCase
from domain.enums import CaseStatus
from storage.db import fetch_next_queued_case, update_case_status


class DbQueueService:
    """QueueService backed by SQLite."""

    def dequeue_next(self) -> Optional[MedicalCase]:
        row = fetch_next_queued_case()
        if row is None:
            return None

        case_id, age, gender, symptoms, status = row

        return MedicalCase(
            id=case_id,
            age=age,
            gender=gender,
            symptoms=symptoms,
            status=CaseStatus[status],
            created_at=datetime.now(timezone.utc),
        )

    def update_status(
        self,
        case_id: int,
        disease: str,
        confidence: float,
        decision: str,
        predictions: Optional[List[Dict]] = None
    ):
        update_case_status(
            case_id=case_id,
            disease=disease,
            confidence=confidence,
            decision=decision,
            predictions=predictions
        )

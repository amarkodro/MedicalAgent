from datetime import datetime
from typing import Optional

from domain.entities import MedicalCase
from domain.enums import CaseStatus
from storage.db import (
    fetch_next_queued_case,
    update_case_status
)


class DbQueueService:
    """
    QueueService koji koristi SQLite (shared storage).
    """

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
            created_at=None,  # Pretpostavljamo da nije potrebno za ovu funkciju
        )

    def update_status(self, case_id: int,disease: str,confidence: float, decision: str):
        update_case_status(case_id, disease, confidence, decision)
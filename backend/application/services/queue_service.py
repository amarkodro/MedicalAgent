from typing import Optional
from domain.entities import MedicalCase
from domain.enums import CaseStatus


class QueueService:
    """
    Ovaj servis predstavlja IZVOR PERCEPTA za agenta.
    """

    def __init__(self, cases: list[MedicalCase]):
        self._cases = cases

    def dequeue_next(self) -> Optional[MedicalCase]:
        for case in self._cases:
            if case.status == CaseStatus.QUEUED:
                case.status = CaseStatus.PROCESSING
                return case
        return None

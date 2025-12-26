from dataclasses import dataclass
from datetime import datetime
from .enums import CaseStatus, Decision, FeedbackResult

@dataclass
class MedicalCase:
    id: int
    age: int
    gender: str
    symptoms: str
    status: CaseStatus
    created_at: datetime

@dataclass
class Prediction:
    case_id: int
    predicted_disease: str
    confidence: float
    decision: Decision
    model_version: str
    created_at: datetime

@dataclass
class Feedback:
    case_id: int
    prediction_id: int
    result: FeedbackResult
    created_at: datetime

@dataclass
class ModelVersion:
    version: str
    trained_at: datetime
    accuracy: float
    active: bool    
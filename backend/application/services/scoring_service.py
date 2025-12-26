from datetime import datetime, timezone
from domain.entities import Prediction, MedicalCase
from domain.rules import DecisionRules
from domain.enums import Decision



class ScoringService:
    """
    Donosi ODLUKU nad jednim medicinskim slučajem.
    """

    def __init__(self, classifier, learning_service, model_version: str):
        self._classifier = classifier
        self._learning_service = learning_service
        self._model_version = model_version

    def score(self, case: MedicalCase) -> Prediction:
        trust = self._learning_service.trust_for_case(case.symptoms)
        predicted_disease, confidence = self._classifier.predict(case, trust)

        decision = DecisionRules.decide(confidence)

        return Prediction(
            case_id=case.id,
            predicted_disease=predicted_disease,
            confidence=confidence,
            decision=decision,
            model_version=self._model_version,
            created_at=datetime.now(timezone.utc)
        )

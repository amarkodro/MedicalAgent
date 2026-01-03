from datetime import datetime, timezone
from typing import List

from domain.entities import Prediction, MedicalCase
from domain.rules import DecisionRules


class ScoringService:
    """Scores a single case and returns predictions."""

    def __init__(self, classifier, learning_service, model_version: str):
        self._classifier = classifier
        self._learning_service = learning_service
        self._model_version = model_version

    def score(self, case: MedicalCase) -> Prediction:
        trust = self._learning_service.trust_for_case(case.symptoms)
        disease, confidence = self._classifier.predict(case, trust)
        decision = DecisionRules.decide(confidence)

        return Prediction(
            case_id=case.id,
            predicted_disease=disease,
            confidence=confidence,
            decision=decision,
            model_version=self._model_version,
            created_at=datetime.now(timezone.utc),
        )

    def score_top_k(self, case: MedicalCase, k: int = 5) -> List[Prediction]:
        trust = self._learning_service.trust_for_case(case.symptoms)
        raw = self._classifier.predict_top_k(case, trust, k)

        preds: List[Prediction] = []
        for disease, confidence in raw:
            decision = DecisionRules.decide(confidence)
            preds.append(
                Prediction(
                    case_id=case.id,
                    predicted_disease=disease,
                    confidence=confidence,
                    decision=decision,
                    model_version=self._model_version,
                    created_at=datetime.now(timezone.utc),
                )
            )
        return preds

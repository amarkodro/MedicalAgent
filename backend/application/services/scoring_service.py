from datetime import datetime, timezone
from typing import List

from domain.entities import Prediction, MedicalCase
from domain.rules import DecisionRules
from storage.db import feedback_stats_for_symptoms_and_disease


class ScoringService:
    def __init__(self, classifier, learning_service, model_version: str):
        self._classifier = classifier
        self._learning_service = learning_service
        self._model_version = model_version

    def score_top_k(self, case: MedicalCase, k: int = 5) -> List[Prediction]:
        raw_results = self._classifier.predict_top_k(case, trust=0.0, k=k)

        base = {disease: conf for disease, conf in raw_results}

        stats = {}
        for disease in base.keys():
            accepted, rejected = feedback_stats_for_symptoms_and_disease(case.symptoms, disease)
            stats[disease] = (accepted, rejected)

        winner = None
        best_acc = 0
        for disease, (acc, rej) in stats.items():
            if acc > best_acc:
                best_acc = acc
                winner = disease

        predictions: List[Prediction] = []

        for disease, base_conf in base.items():
            acc, rej = stats[disease]

            delta = 0.0

            if winner and disease == winner:
                # boost raste s accepted
                delta += min(0.25, 0.08 + 0.04 * acc)

            elif winner and disease != winner:

                delta -= min(0.12, 0.03 + 0.02 * best_acc)

            if rej >= 1:
                delta -= min(0.20, 0.06 + 0.03 * rej)

            confidence = max(0.05, min(0.99, base_conf + delta))
            decision = DecisionRules.decide(confidence)

            predictions.append(
                Prediction(
                    case_id=case.id,
                    predicted_disease=disease,
                    confidence=confidence,
                    decision=decision,
                    model_version=self._model_version,
                    created_at=datetime.now(timezone.utc),
                )
            )

        predictions.sort(key=lambda p: p.confidence, reverse=True)
        return predictions[:k]

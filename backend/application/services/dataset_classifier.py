import csv
from collections import Counter
from typing import List, Tuple

from domain.entities import MedicalCase
from application.services.learning_service import LearningService


class DatasetClassifier:
    """
    Simple CSV-driven classifier (no ML).
    Uses symptom overlap scoring + feedback filter.
    """

    def __init__(self, csv_path: str, learning_service: LearningService):
        self.symptom_map = {}  # symptoms_string -> [disease,...]
        self.learning_service = learning_service
        self._load(csv_path)

    def _load(self, path: str):
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                symptoms = row["Simptomi"].lower().strip()
                disease = row["Bolest"].strip()

                if not symptoms or not disease:
                    continue

                self.symptom_map.setdefault(symptoms, [])
                self.symptom_map[symptoms].append(disease)

    @staticmethod
    def _split_set(symptoms: str) -> set:
        return {s.strip() for s in symptoms.lower().split(",") if s.strip()}

    def predict(self, case: MedicalCase, trust: float = 0.5) -> Tuple[str, float]:
        results = self.predict_top_k(case, trust, k=1)
        if not results:
            return "Unknown", 0.2
        return results[0]

    def predict_top_k(
        self,
        case: MedicalCase,
        trust: float,
        k: int = 5
    ) -> List[Tuple[str, float]]:
        """Return up to K diseases with confidence."""

        case_set = self._split_set(case.symptoms)
        if not case_set:
            return [("Unknown", 0.2)]

        disease_scores = {}  # disease -> best_score

        for dataset_symptoms, diseases in self.symptom_map.items():
            dataset_set = self._split_set(dataset_symptoms)
            if not dataset_set:
                continue

            overlap = case_set & dataset_set
            if not overlap:
                continue

            # Jaccard (penalizes extra symptoms on either side)
            union = case_set | dataset_set
            base_score = len(overlap) / len(union)

            # pick most common disease for that symptom row OR spread across all in that row
            for disease in set(diseases):
                if self.learning_service.is_disease_rejected_for_symptoms(case.symptoms, disease):
                    continue
                prev = disease_scores.get(disease, 0.0)
                disease_scores[disease] = max(prev, base_score)

        if not disease_scores:
            return [("Unknown", 0.2)]

        results: List[Tuple[str, float]] = []
        multiplier = 0.5 + trust  # ~1.0 when trust=0.5
        for disease, score in disease_scores.items():
            confidence = score * multiplier
            confidence = min(confidence, 1.0)
            results.append((disease, confidence))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:k]

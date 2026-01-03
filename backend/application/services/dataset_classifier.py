import csv
from collections import Counter, defaultdict
from typing import List, Tuple

from domain.entities import MedicalCase
from application.services.learning_service import LearningService


class DatasetClassifier:
    """
    Simple CSV-driven classifier (no ML).
    Uses symptom overlap scoring + feedback filter.
    """


class DatasetClassifier:
    def __init__(self, csv_path: str, learning_service):
        self.learning_service = learning_service
        self.symptom_to_diseases = defaultdict(Counter)  # symptom -> Counter(disease -> freq)
        self._load(csv_path)

    def _load(self, path: str):
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                symptoms_raw = row.get("Simptomi", "").lower().strip()
                disease = row.get("Bolest", "").strip()

                if not symptoms_raw or not disease:
                    continue

                symptoms_list = [s.strip() for s in symptoms_raw.split(",") if s.strip()]
                for symptom in symptoms_list:
                    self.symptom_to_diseases[symptom][disease] += 1



    @staticmethod
    def _split_set(symptoms: str) -> set:
        return {s.strip() for s in symptoms.lower().split(",") if s.strip()}

    def predict(self, case: MedicalCase, trust: float = 0.5) -> Tuple[str, float]:
        results = self.predict_top_k(case, trust, k=1)
        if not results:
            return "Unknown", 0.2
        return results[0]

    def predict_top_k(self, case, trust: float, k: int = 5) -> List[Tuple[str, float]]:
        input_symptoms = [s.strip() for s in case.symptoms.lower().split(",") if s.strip()]
        if not input_symptoms:
            return [("Unknown", 0.2)]

        disease_score = Counter()

        # 1) boduj bolesti preko svakog simptoma
        for symptom in input_symptoms:
            for disease, freq in self.symptom_to_diseases.get(symptom, {}).items():
                if self.learning_service.is_disease_rejected_for_symptoms(case.symptoms, disease):
                    continue
                disease_score[disease] += freq

        if not disease_score:
            return [("Unknown", 0.2)]

        # 2) normalizacija: koliko je jako u odnosu na broj unesenih simptoma
        # max_score ≈ kada se bolest pojavljuje u svim simptomima često
        max_score = max(disease_score.values())

        results = []
        for disease, score in disease_score.items():
            # core confidence (0-1): relativno prema najboljoj bolesti
            base_conf = score / max_score

            # dodatno: penalizuj ako je user unio puno simptoma a bolest "ne pokriva"
            # (ovo sprječava lažnih 100%)
            coverage = 0
            for symptom in input_symptoms:
                if disease in self.symptom_to_diseases.get(symptom, {}):
                    coverage += 1
            coverage_ratio = coverage / len(input_symptoms)

            confidence = 0.7 * base_conf + 0.3 * coverage_ratio  # miks ranking + coverage

            # trust utiče, ali ne smije pumpati do 1.0 lako
            confidence = confidence * (0.6 + 0.4 * trust)
            confidence = min(confidence, 0.95)  # cap da ne iskače 100% stalno

            results.append((disease, confidence))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:k]



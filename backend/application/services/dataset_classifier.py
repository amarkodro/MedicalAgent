import csv
from collections import Counter
from domain.entities import MedicalCase
from application.services.learning_service import LearningService





class DatasetClassifier:
    """
    Jednostavan data-driven classifier baziran na CSV-u.
    Uči kroz feedback (bez ML-a).
    """

    def __init__(self, csv_path: str, learning_service: LearningService):
        self.symptom_map = {}
        self.learning_service = learning_service
        self._load(csv_path)

    def _load(self, path: str):
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                symptoms = row["Simptomi"].lower()
                disease = row["Bolest"]

                self.symptom_map.setdefault(symptoms, [])
                self.symptom_map[symptoms].append(disease)

    def predict(self, case: MedicalCase, trust: float = 0.5):
        case_symptoms_set = set(
            s.strip() for s in case.symptoms.lower().split(",")
        )

        candidates = []

        # -------- SENSE + THINK --------
        for dataset_symptoms, diseases in self.symptom_map.items():
            dataset_set = set(s.strip() for s in dataset_symptoms.split(","))
            overlap = case_symptoms_set & dataset_set
            score = len(overlap) / len(dataset_set)

            if score > 0:
                disease = Counter(diseases).most_common(1)[0][0]

                # -------- LEARN FILTER --------
                if self.learning_service.is_disease_rejected_for_symptoms(
                    case.symptoms, disease
                ):
                    continue  # preskoči lošu bolest

                candidates.append((disease, score))

        # -------- ACT --------
        if not candidates:
            base_disease = "Unknown"
            base_confidence = 0.2
        else:
            base_disease, base_confidence = max(
                candidates, key=lambda x: x[1]
            )

        # trust utiče na confidence
        base_confidence = base_confidence * (0.5 + trust)
        base_confidence = min(base_confidence, 1.0)

        return base_disease, base_confidence

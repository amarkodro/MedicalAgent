import csv
from collections import Counter
from domain.entities import MedicalCase




class DatasetClassifier:
    """
    Jednostavan data-driven classifier baziran na CSV-u.
    Ne koristi ML – koristi statistiku iz dataseta.
    """

    def __init__(self, csv_path: str):
        self.symptom_map = {}
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

        best_match = None
        best_score = 0.0

        for dataset_symptoms, diseases in self.symptom_map.items():
            dataset_set = set(s.strip() for s in dataset_symptoms.split(","))
            overlap = case_symptoms_set & dataset_set
            score = len(overlap) / len(dataset_set)

            if score > best_score:
                best_score = score
                best_match = Counter(diseases).most_common(1)[0][0]

        if best_match is None:
            base_confidence = 0.2
            base_disease = "Unknown"
        else:
            base_confidence = best_score
            base_disease = best_match

        base_confidence = min(base_confidence, 1.0)

        adjustment = (trust - 0.5) * 2   # [-1, +1]
        base_confidence += adjustment * 0.3
        base_confidence = max(0.0, min(base_confidence, 1.0))

        return base_disease, base_confidence

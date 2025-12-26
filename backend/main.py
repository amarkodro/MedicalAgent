from datetime import datetime, timezone
from domain.entities import MedicalCase
from domain.enums import CaseStatus
from application.services.queue_service import QueueService
from application.services.scoring_service import ScoringService
from application.services.learning_service import LearningService
from application.runners.scoring_runner import ScoringAgentRunner
from application.runners.retrain_runner import RetrainAgentRunner

now = datetime.now(timezone.utc)

# -------------------------------------------------
# Dummy ML classifier (simulacija modela)
# -------------------------------------------------
class DummyClassifier:
    def predict(self, case: MedicalCase):
        # simulacija ML predikcije
        return "Flu", 0.4   # namjerno nisko (da vidimo reject)


def main():
    # ------------------ STANJE SVIJETA ------------------
    cases = [
        MedicalCase(
            id=1,
            age=25,
            gender="M",
            symptoms="fever, cough",
            status=CaseStatus.QUEUED,
            created_at=now
        )
    ]

    # ------------------ SERVISI ------------------
    queue_service = QueueService(cases)
    learning_service = LearningService()
    scoring_service = ScoringService(
        classifier=DummyClassifier(),
        model_version="v1"
    )

    # ------------------ RUNNERI ------------------
    scoring_runner = ScoringAgentRunner(
        queue_service=queue_service,
        scoring_service=scoring_service
    )

    retrain_runner = RetrainAgentRunner(
        learning_service=learning_service,
        rejection_threshold=0.3
    )

    # ------------------ AGENT TICK ------------------
    prediction = scoring_runner.tick()

    if prediction:
        print("Agent decision:", prediction.decision)

        # ------------------ FEEDBACK ------------------
        # simuliramo da je odluka bila loša
        learning_service.add_feedback(
            case_id=prediction.case_id,
            prediction_id=1,
            accepted=False
        )

    # ------------------ LEARN TICK ------------------
    should_retrain = retrain_runner.tick()

    print("Rejection rate:", learning_service.rejection_rate())
    print("Should retrain:", should_retrain)


if __name__ == "__main__":
    main()

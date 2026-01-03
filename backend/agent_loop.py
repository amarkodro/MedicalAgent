import time

from storage.db import init_db
from application.services.scoring_service import ScoringService
from application.services.learning_service import LearningService
from application.runners.scoring_runner import ScoringAgentRunner
from application.runners.retrain_runner import RetrainAgentRunner
from application.services.db_queue_service import DbQueueService
from application.services.dataset_classifier import DatasetClassifier


def run_agent():
    init_db()

    queue_service = DbQueueService()
    learning_service = LearningService()

    classifier = DatasetClassifier(
        "data/Medicina_Dataset.csv",
        learning_service
    )

    scoring_service = ScoringService(
        classifier=classifier,
        learning_service=learning_service,
        model_version="dataset-v1",
    )

    scoring_runner = ScoringAgentRunner(
        queue_service=queue_service,
        scoring_service=scoring_service
    )

    retrain_runner = RetrainAgentRunner(
        learning_service=learning_service,
        rejection_threshold=0.3
    )

    print("🤖 Agent started")

    try:
        while True:
            prediction = scoring_runner.tick()
            if prediction:
                print(
                    f"Decision: {prediction.decision.name} | "
                    f"Disease: {prediction.predicted_disease} | "
                    f"Confidence: {prediction.confidence:.2f}"
                )

            if retrain_runner.tick():
                print("🔁 Retrain required")
                learning_service.reset()
                retrain_runner.reset()

            time.sleep(2)
    except KeyboardInterrupt:
        print("🛑 Agent stopped gracefully")


if __name__ == "__main__":
    run_agent()

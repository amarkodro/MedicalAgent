from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import json

from storage.db import init_db, insert_case, get_case_by_id, count_feedback, insert_feedback

app = FastAPI(title="MedicalAIAgent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()


class MedicalCaseCreateDto(BaseModel):
    age: int
    gender: str
    symptoms: str


class FeedbackCreateDto(BaseModel):
    case_id: int
    disease: str
    accepted: bool


@app.post("/cases")
def create_case(dto: MedicalCaseCreateDto):
    case_id = insert_case(
        age=dto.age,
        gender=dto.gender,
        symptoms=dto.symptoms
    )

    return {"case_id": case_id, "status": "QUEUED"}


@app.post("/feedback")
def submit_feedback(dto: FeedbackCreateDto):
    insert_feedback(
        case_id=dto.case_id,
        disease=dto.disease,
        accepted=dto.accepted
    )
    return {"status": "feedback received"}


@app.get("/stats")
def get_stats():
    accepted, rejected = count_feedback()
    total = accepted + rejected
    rejection_rate = (rejected / total) if total > 0 else 0.0

    return {
        "accepted": accepted,
        "rejected": rejected,
        "total": total,
        "rejection_rate": rejection_rate
    }


@app.get("/cases/{case_id}")
def get_case(case_id: int):
    row = get_case_by_id(case_id)
    if not row:
        return {"error": "Case not found"}

    predictions = json.loads(row[8]) if row[8] else []

    return {
        "id": row[0],
        "age": row[1],
        "gender": row[2],
        "symptoms": row[3],
        "status": row[4],
        "main_prediction": {
            "disease": row[5],
            "confidence": row[6],
            "decision": row[7]
        } if row[4] == "DIAGNOSED" else None,
        "other_predictions": predictions
    }

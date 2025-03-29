from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import sqlite3
from auth import get_db

router = APIRouter()

class QuestionCreate(BaseModel):
    user_id: int
    question: str
    answer: str
    validation_result: str
    confidence_score: float

@router.get("/users/")
def get_users(db=Depends(get_db)):
    """Get all users"""
    users = db.execute("SELECT id, username, email FROM users").fetchall()

    if not users:
        return []
    
    return [{"id": user["id"], "username": user["username"], "email": user["email"]} for user in users]

@router.get("/questions/")
def get_all_questions(db=Depends(get_db)):
    """Retrieve all stored question-answer pairs"""
    qa_pairs = db.execute("SELECT id, user_id, question, answer, validation_result, confidence_score FROM qa_pairs").fetchall()

    if not qa_pairs:
        return []

    return [{
        "id": qa["id"],
        "user_id": qa["user_id"],
        "question": qa["question"],
        "answer": qa["answer"],
        "validation_result": qa["validation_result"],
        "confidence_score": qa["confidence_score"]
    } for qa in qa_pairs]

@router.post("/questions/")
def store_question_answer(question_data: QuestionCreate, db=Depends(get_db)):
    """Store a new question-answer pair"""
    # Check if user exists
    user = db.execute("SELECT id FROM users WHERE id = ?", (question_data.user_id,)).fetchone()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid user_id: User does not exist")

    try:
        db.execute("INSERT INTO qa_pairs (user_id, question, answer, validation_result, confidence_score) VALUES (?, ?, ?, ?, ?)",
                   (question_data.user_id, question_data.question, question_data.answer, question_data.validation_result, question_data.confidence_score))
        db.commit()
        return {"message": "Stored successfully"}
    except sqlite3.IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error storing data")
    
@router.get("/questions/{user_id}")
def get_questions(user_id: int, db=Depends(get_db)):
    """Get all questions for a user"""
    questions = db.execute("SELECT id, question, answer, validation_result, confidence_score FROM qa_pairs WHERE user_id = ?", (user_id,)).fetchall()
    if not questions:
        raise HTTPException(status_code=404, detail="No questions found for this user")
    return [{
        "id": q["id"],
        "question": q["question"],
        "answer": q["answer"],
        "validation_result": q["validation_result"],
        "confidence_score": q["confidence_score"],
    } for q in questions]
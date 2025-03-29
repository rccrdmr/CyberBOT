import asyncio
import time
import logging
import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from followup_detector import is_followup_question
from llm_infer import get_response, augment_question
from routes import router as api_router
from auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from backend.answer_retriever import retrieve_qa_context, load_faiss_index
from ontology_validator import ontology_validation

# Setup FastAPI
app = FastAPI(title="CyberBot RAG API", version="1.0")
app.include_router(api_router)
app.include_router(auth_router)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging Configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# Pydantic request/response models
class QueryRequest(BaseModel):
    user_id: int
    question: str

class QueryResponse(BaseModel):
    question: str
    retrieval_context: str
    generated_answer: str
    validation_result: str
    confidence_score: float


async def retrieve_and_answer(user_id, question):
    """
    Augments the user question using chat history,
    retrieves context from FAISS using the augmented question,
    and generates an answer using the original question.
    """
    # Step 1: Augment question for retrieval
    is_followup, reason = is_followup_question(question)
    if is_followup:
        logger.info(f"✍️ Augmenting question — follow-up detected. Reason: {reason}")
        augmented_question = await asyncio.to_thread(augment_question, user_id, question)
    else:
        logger.info(f"✅ No augmentation — Reason: {reason}")
        augmented_question = question

    # Step 2: Use augmented question for RAG context retrieval
    prompts = retrieve_qa_context([augmented_question])  
    retrieved_context = prompts[0]  # First retrieved prompt
    
    # Step 3: Use original question in prompt (not augmented version)
    answer_prompt = f"""
    You are an expert in cybersecurity and cloud computing.
    {retrieved_context}
    QUESTION: {question}
    ANSWER:
    """
    
    # Step 4: Send prompt to model
    response = await asyncio.to_thread(get_response, input_text=answer_prompt, user_id=user_id, max_tokens=300)
    generated_answer = response.choices[0].message.content.strip() if response and response.choices else "I'm sorry, but I couldn't generate a response. Please try again."

    return retrieved_context, generated_answer, augmented_question


@app.post("/query", response_model=QueryResponse)
async def query_cyberbot(request: QueryRequest):
    user_id = request.user_id
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    logger.info(f"Received query: {question}")

    retrieved_context, generated_answer, rewritten_question = await retrieve_and_answer(user_id, question)

    logger.info(f"📝 Validating QA Pair:\nQuestion (validated): {rewritten_question}\nAnswer: {generated_answer}")

    validation_data = await asyncio.to_thread(ontology_validation, rewritten_question, generated_answer, user_id)
    validation_result = validation_data.get("validation_result")
    confidence_score = validation_data.get("confidence_score")

    if validation_result == "Not Pass":
        return QueryResponse(
            question=question,
            retrieval_context=retrieved_context,
            generated_answer="⚠️ This answer could not be validated against the ontology. Please refine your question.",
            validation_result=validation_result,
            confidence_score=confidence_score,
        )

    return QueryResponse(
        question=question,
        retrieval_context=retrieved_context,
        generated_answer=generated_answer,
        validation_result=validation_result,
        confidence_score=confidence_score,
    )
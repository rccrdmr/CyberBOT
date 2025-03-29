import os
import torch
import pandas as pd
import numpy as np
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer

ROOT_DIR = Path(__file__).resolve().parent
kb_path = ROOT_DIR / "dataset" / "kb"

# Set device for computation
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load SentenceTransformer model
def load_qa_retriever(model_name='BAAI/bge-large-en-v1.5'):
    model = SentenceTransformer(model_name, device=device)
    return model

# Load KB from CSV
def load_qa_kb(name='kb.csv', path=kb_path):
    kb_path = os.path.join(path, name)
    kb = pd.read_csv(kb_path)
    return kb

# Compute embeddings for text pairs
def compute_embedding(texts, model):
    embeddings = model.encode(texts, normalize_embeddings=True)
    return np.array(embeddings, dtype=np.float32)  # Convert to NumPy array

if __name__ == '__main__':
    print("⚡ Loading embedding model...")
    model = load_qa_retriever()

    print("⚡ Loading KB dataset...")
    kb = load_qa_kb()

    # Ensure the "Question" and "Answer" columns exist in the KB
    if "Question" not in kb.columns or "Answer" not in kb.columns:
        raise ValueError("❌ 'Question' or 'Answer' column not found in kb.csv!")

    print("⚡ Generating embeddings for KB question-answer pairs...")

    # Concatenate Question + Answer for embeddings
    qa_texts = kb.apply(lambda row: f"Q: {row['Question']} A: {row['Answer']}", axis=1).tolist()

    # Compute embeddings
    qa_embeddings = compute_embedding(qa_texts, model)

    # Save KB embeddings
    np.save("qa_embeddings.npy", qa_embeddings)
    print(f"✅ qa embeddings saved to qa_embeddings.npy with shape {qa_embeddings.shape}")

    # Create metadata for KB
    kb_metadata = []
    for i, row in kb.iterrows():
        kb_metadata.append({
            "qid": row.get("QID", f"Q-{i}"),  # Use QID if available, else assign a default
            "question": row["Question"],
            "answer": row["Answer"],
            "ontology": row.get("Ontology", "unknown"),
            "relation": row.get("Relation", "unknown"),
            "source": "kb.csv"
        })

    # Save KB metadata
    with open("qa_metadata.json", "w") as f:
        json.dump(kb_metadata, f, indent=4)
    print("✅ QA metadata saved to qa_metadata.json")

import faiss
import numpy as np
from pathlib import Path

# Load document and QA embeddings
ROOT_DIR = Path(__file__).resolve().parent
qa_embeddings = np.load(ROOT_DIR / "backend" / "qa_embeddings.npy").astype(np.float32)

# Create FAISS indexes
dimension = qa_embeddings.shape[1]
qa_index = faiss.IndexFlatL2(dimension)
qa_index.add(qa_embeddings)
faiss.write_index(qa_index, "qa_faiss.index")

print("✅ QA FAISS indexes stored.")

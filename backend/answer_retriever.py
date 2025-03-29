import faiss
import numpy as np
import json
from sentence_transformers import SentenceTransformer

# Load Sentence Transformer model for encoding queries
MODEL_NAME = 'BAAI/bge-large-en-v1.5'
model = SentenceTransformer(MODEL_NAME)

# Load FAISS indexes
def load_faiss_index(index_path, embeddings_path):
    """
    Load FAISS index and embeddings.
    """
    index = faiss.read_index(index_path)
    embeddings = np.load(embeddings_path).astype(np.float32)
    return index, embeddings

# Load metadata
def load_metadata(metadata_path):
    with open(metadata_path, "r") as f:
        return json.load(f)

# Paths to stored embeddings and indexes
QA_INDEX_PATH = "qa_faiss.index"
QA_EMBEDDINGS_PATH = "qa_embeddings.npy"
QA_METADATA_PATH = "qa_metadata.json"

# Load FAISS indexes and metadata
qa_index, qa_embeddings = load_faiss_index(QA_INDEX_PATH, QA_EMBEDDINGS_PATH)
qa_metadata = load_metadata(QA_METADATA_PATH)

print(f"✅ FAISS indexes loaded: {qa_index.ntotal} QA embeddings.")

def apply_prompt(query, document, usr_prompt=None):
    """
    Formats the retrieved context into a structured prompt.
    """
    if not usr_prompt:
        usr_prompt = (
            "Answer the user's QUESTION using the DOCUMENT text above.\n"
            "Keep your answer grounded in the facts of the DOCUMENT.\n"
            "If the DOCUMENT does not contain the facts to answer the QUESTION, "
            "give a response based on your knowledge."
        )

    result = (
        "DOCUMENT:\n{0}\n\n"
        "QUESTION:\n{1}\n\n"
        "INSTRUCTIONS:\n{2}\n\n"
        "Answer concisely and factually without extra commentary:"
    ).format(document, query, usr_prompt)

    return result

def retrieve_qa_context(queries, top_k=3):
    """
    Retrieves relevant QA pairs and document text to generate structured prompts.
    """
    prompt_list = []

    for query in queries:
        # Encode query
        query_embedding = model.encode([query], normalize_embeddings=True).astype(np.float32)

        # Search FAISS QA index
        qa_distances, qa_indices = qa_index.search(query_embedding, top_k)
        best_qa_matches = [qa_metadata[i] for i in qa_indices[0]]


        # Construct document text from retrieved results
        retrieved_docs = [
            f"Q: {qa['question']} A: {qa['answer']}" for qa in best_qa_matches
        ]

        document_text = "\n".join(retrieved_docs)

        # Apply prompt formatting
        prompt = apply_prompt(query, document_text)
        prompt_list.append(prompt)

    return prompt_list

if __name__ == '__main__':
    queries = [
        "What factors determine the severity of a vulnerability?",
        "How does access control work in cloud environments?",
        "What are common cyber threats to databases?"
    ]

    prompt_list = retrieve_qa_context(queries)

    for i, prompt in enumerate(prompt_list):
        print(f"\n🔹 **Generated Prompt {i+1}:**\n")
        print(prompt)
        print('-----------------------------------')

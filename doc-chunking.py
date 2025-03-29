import os
import glob
import logging
import PyPDF2
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List
from pathlib import Path

# Logging Configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Directory containing PDF files
ROOT_DIR = Path(__file__).resolve().parent
KB_DIRECTORY = ROOT_DIR / "dataset" / "kb"
PDF_FILES = glob.glob(os.path.join(KB_DIRECTORY, "*.pdf"))

# Define chunking function
def chunk_text(text: str, chunk_size: int = 500) -> List[str]:
    """
    Splits a text into chunks of a given size while preserving sentence boundaries.
    """
    sentences = text.split('.')
    chunks = []
    current_chunk = []
    current_size = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue  # Skip empty sentences

        if current_size + len(sentence) > chunk_size and current_chunk:
            chunks.append('. '.join(current_chunk) + '.')
            current_chunk = []
            current_size = 0

        current_chunk.append(sentence)
        current_size += len(sentence)

    if current_chunk:
        chunks.append('. '.join(current_chunk) + '.')

    return [c for c in chunks if len(c.strip()) > 50]  # Keep only substantial chunks

# Define a class to store document chunks
class Document:
    def __init__(self, content, source, page_number, category="unclassified"):
        self.content = content
        self.source = source
        self.page_number = page_number
        self.category = category
        self.embedding = None  # Placeholder for embedding

# Process PDFs and create document chunks
documents = []
for pdf_path in PDF_FILES:
    logger.info(f"Processing: {os.path.basename(pdf_path)}")

    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)

        for page_num in range(len(pdf_reader.pages)):
            text = pdf_reader.pages[page_num].extract_text()
            chunks = chunk_text(text)

            logger.info(f"Page {page_num + 1}: {len(chunks)} chunks created.")

            for chunk in chunks:
                doc = Document(
                    content=chunk,
                    source=os.path.basename(pdf_path),
                    page_number=page_num + 1
                )
                documents.append(doc)

logger.info(f"Total documents created: {len(documents)}")

# Display sample chunks
for i in range(min(3, len(documents))):
    logger.info(f"Document {i+1}:")
    logger.info(f"Source: {documents[i].source}")
    logger.info(f"Page: {documents[i].page_number}")
    logger.info(f"Content preview: {documents[i].content[:200]}...")

# Initialize the embedding model
logger.info("Loading embedding model...")
model = SentenceTransformer('BAAI/bge-large-en-v1.5')

def create_embeddings_batch(docs, batch_size=8):
    """
    Generates embeddings for document chunks in batches.
    """
    logger.info(f"Creating embeddings for {len(docs)} documents in batches of {batch_size}")

    for i in range(0, len(docs), batch_size):
        batch = docs[i:i + batch_size]
        texts = [doc.content for doc in batch]

        # Generate embeddings
        embeddings = model.encode(texts, normalize_embeddings=True)

        # Assign embeddings to documents
        for doc, embedding in zip(batch, embeddings):
            doc.embedding = embedding

        logger.info(f"Processed batch {i//batch_size + 1}, documents {i} to {min(i+batch_size, len(docs))}")

        # Print shape of first embedding in batch as a sanity check
        if i == 0:
            logger.info(f"Embedding shape: {embeddings[0].shape}")

# Generate embeddings for all documents
create_embeddings_batch(documents)

# Verify embeddings
logger.info("Embedding verification:")
logger.info(f"First document embedding shape: {documents[0].embedding.shape}")
logger.info(f"First document embedding sample: {documents[0].embedding[:5]}...")

# Save embeddings for later use
np.save("document_embeddings.npy", np.array([doc.embedding for doc in documents]))
logger.info("Embeddings saved to document_embeddings.npy")

# Save metadata
import json
metadata = [
    {"content": doc.content, "source": doc.source, "page_number": doc.page_number, "category": doc.category}
    for doc in documents
]
with open("document_metadata.json", "w") as f:
    json.dump(metadata, f, indent=4)
logger.info("Metadata saved to document_metadata.json")

logger.info("✅ PDF processing and embedding generation completed!")

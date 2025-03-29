# 🛡️ CyberBOT

CyberBOT is an AI-powered educational assistant built to support student learning in **Cybersecurity** through interactive question answering, ontology validation, and personalized feedback.

This project is developed as part of the **ACL 2025 Demonstration Track**.

---

## 🎓 Purpose

CyberBOT is designed to provide students with accurate and context-aware answers to cybersecurity-related questions by combining:

- 🔍 **Retrieval-Augmented Generation (RAG)** using QA pairs
- 🧠 **Large Language Models (LLMs)** via Together API (LLaMA-3 70B)
- 📚 **Ontology-based validation** to ensure factual correctness
- 👤 **User-level tracking** and learning history
- 🖼️ **Streamlit frontend** with a FastAPI backend

---

## 📚 Dataset

CyberBOT uses a publicly available QA dataset focused on cybersecurity:

- [AISecKG Cybersecurity QA Dataset](https://github.com/garima0106/AISecKG-cybersecurity-dataset)

The dataset includes hundreds of question-answer pairs grounded in cybersecurity concepts, including threat modeling, cryptography, system vulnerabilities, cloud security, and more.

---

## 🚀 Features

- ✅ Ask cybersecurity questions and get LLM-generated answers
- ✅ Follow-up questions are automatically rewritten for clarity
- ✅ Retrieves relevant QA context using FAISS similarity search
- ✅ Validates each answer against a domain ontology
- ✅ Tracks per-user question and answer history in a local DB

---

## 📁 Project Structure

```
CyberBOT/
├── backend/                  # FastAPI backend
│   ├── api.py                # Main app entrypoint
│   ├── answer_retriever.py   # Retrieves context using FAISS + QA dataset
│   ├── auth.py               # User auth system (register/login)
│   ├── db.py, models.py      # SQLAlchemy models + DB setup
│   ├── llm_infer.py          # Calls LLM (Together API)
│   ├── followup_detector.py  # Detects vague/follow-up questions
│   ├── ontology_validator.py # Validates answers using ontology
│   ├── routes.py             # Stores QA history to DB
│   ├── utils.py, config.py
│
├── frontend/                 # Streamlit UI
│   ├── main.py               # Landing page
│   └── pages/
│       ├── access.py         # Login/signup interface
│       └── chat.py           # Chat interface
│
├── dataset/
│   ├── kb/kb.csv             # Cybersecurity QA dataset
│   └── ontology/             # Ontology for answer validation
│       ├── ontology.txt
│       └── ontology.csv
│
├── qapair-embedder.py        # Script to encode QA pairs + save metadata
├── faiss_index.py            # Builds FAISS index from QA embeddings
├── requirements.txt          # Python dependencies
└── README.md                 # You're here!
```

---

## ⚙️ Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/rccrdmr/CyberBOT.git
cd CyberBOT
```

### 2. Set Up the Environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Add Your API Key

Set your Together API key:

```bash
export TOGETHER_API_KEY="your-api-key"
```

### 4. Generate QA Embeddings

```bash
python qapair-embedder.py
```

This generates:
- `qa_embeddings.npy`
- `qa_metadata.json`

### 5. Build the FAISS Index

```bash
python faiss_index.py
```

This creates:
- `qa_faiss.index`

### 6. Run the Backend

```bash
cd backend
uvicorn api:app --reload
```

### 7. Run the Frontend

```bash
cd frontend
streamlit run main.py
```

---

## 🧠 Retrieval and Answer Pipeline

1. User submits a question.
2. If it's vague or follow-up, it is rewritten via LLM.
3. FAISS retrieves similar QA examples from the cybersecurity dataset.
4. A context-aware prompt is built for the LLM.
5. The answer is validated using the domain ontology.
6. Validated answers are stored and shown in the UI.

---

## ✅ Requirements

Major dependencies:

- `fastapi`, `uvicorn`, `streamlit`
- `sentence-transformers`, `faiss-cpu`
- `together`, `pydantic`, `sqlalchemy`, `passlib`

Install with:

```bash
pip install -r requirements.txt
```

---

## 🧑‍💻 Author

- Riccardo De Maria ([GitHub @rccrdmr](https://github.com/rccrdmr))  
- Arizona State University – Data Mining and Machine Learning Lab (DMML)

---

## 📜 License

MIT License — Open for academic and educational use.

---

*“The best defense against cyberattacks is a well-trained mind and a vigilant eye.” – Dr. Bruce Schneier*

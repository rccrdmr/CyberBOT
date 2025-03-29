# 🛡️ CyberBOT

CyberBOT is an AI-powered educational assistant designed to help students learn **Cybersecurity** and **Cloud Computing** through question answering, validation, and personalized guidance.

Built with:
- 🔍 Retrieval-Augmented Generation (RAG)
- 🧠 LLM (LLaMA-3 70B via Together API)
- 🧾 Ontology-based Answer Validation
- 🧑‍🎓 User login and learning history
- 🖼️ Streamlit Frontend + FastAPI Backend

---

## 🚀 Features

✅ Ask questions about cybersecurity & cloud  
✅ Automatically augments follow-up questions  
✅ Retrieves QA context from a public dataset  
✅ Uses LLMs to generate informative answers  
✅ Validates answers against an ontology  
✅ Tracks user history in a local database  

---

## 📁 Project Structure

```
CyberBOT/
├── backend/             # FastAPI backend
│   ├── api.py
│   ├── answer_retriever.py
│   ├── llm_infer.py
│   ├── ontology_validator.py
│   ├── auth.py, db.py, models.py, routes.py
│   └── utils.py, config.py
│
├── frontend/            # Streamlit app
│   ├── main.py
│   └── pages/
│       ├── access.py
│       └── chat.py
│
├── dataset/             # Ontology + QA pairs
│   └── ontology/
│       ├── ontology.txt
│       └── ontology.csv
│
├── faiss_index.py       # Index builder script
├── qapair-embedder.py   # Embedding script for QA pairs
├── requirements.txt     # Python dependencies
└── README.md
```

---

## ⚙️ Getting Started

### 1. Clone the Repo

```bash
git clone https://github.com/rccrdmr/CyberBOT.git
cd CyberBOT
```

### 2. Set Up Environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Set Up `.env` or Export API Key

```bash
export TOGETHER_API_KEY="your-key-here"
```

### 4. Embed and Index QA Dataset

```bash
python qapair-embedder.py
```

### 5. Run Backend

```bash
cd backend
uvicorn api:app --reload
```

### 6. Run Frontend

```bash
cd frontend
streamlit run main.py
```

---

## 🧠 Dataset and Ontology

- **QA Pairs**: A curated set of question-answer pairs on cybersecurity and cloud.
- **Ontology**: Used to validate AI-generated answers for factual consistency.

---

## 📝 TODO

- [ ] Add support for saving bookmarks or favorite answers  
- [ ] Enable admin upload of new QA pairs  
- [ ] Add model confidence explanations  

---

## 🧑‍💻 Authors

- Riccardo De Maria ([@rccrdmr](https://github.com/rccrdmr))  
- ASU Data Mining and Machine Learning Lab (DMML)

---

## 📜 License

MIT License — feel free to use, extend, and contribute!

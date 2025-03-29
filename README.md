
# 🛡️ CyberBOT: An AI-Powered Educational Assistant for Cybersecurity Learning

CyberBOT is a **domain-specific AI assistant** designed to support student learning in **Cybersecurity** and **Cloud Computing**, with a strong emphasis on **trustworthy AI practices** such as:

- ✅ Ontology-based Answer Validation  
- ✅ Domain-Specific Reasoning (Cybersecurity vs. Cloud)  
- ✅ Context Tracking for Follow-Up Questions  

This system goes **beyond traditional RAG** by ensuring factual consistency, intent clarification, and meaningful multi-turn interaction.

---

## 📸 System Architecture

![System Pipeline](./illustrations/pipeline.png)

---

## 🧠 Key Features

| Component         | Model Name                                        | Purpose                                                        |
|------------------|---------------------------------------------------|----------------------------------------------------------------|
| **Embedding**     | `BAAI/bge-large-en-v1.5`                          | Vector search via FAISS for question matching                  |
| **Answering**     | `meta-llama/Llama-3.3-70B-Instruct-Turbo`         | Generates informative answers                                  |
| **Intent Rewrite**| `meta-llama/Llama-3.3-70B-Instruct-Turbo`         | Rewrites vague or follow-up questions to standalone form       |
| **Validation**    | `meta-llama/Llama-3.3-70B-Instruct-Turbo`         | Verifies answers against cybersecurity ontology                |

---

## 🔍 Use Case

![Use Case Illustration](./illustrations/case.png)

CyberBOT allows users to engage in natural conversation around cybersecurity concepts. Each generated answer is validated for factual alignment using a curated **ontology**.

---

## 💡 Why CyberBOT is Different

Regular RAG systems retrieve content and generate answers, but may hallucinate or misinterpret vague questions. **CyberBOT is different**:

- ✅ **Follow-up Detection**: Detects if a question lacks context and rewrites it  
- ✅ **Ontology Validation**: Guarantees answers are grounded in a knowledge base  
- ✅ **Domain-Specific Reasoning**: Handles multiple domains (e.g., Cyber vs. Cloud)

> 📌 For this repo, we focus on the **Cybersecurity QA dataset**:  
> [AISecKG Cybersecurity QA Dataset](https://github.com/garima0106/AISecKG-cybersecurity-dataset)

---

## 🧠 Example Pipeline Flow

![Pipeline Illustration](./illustrations/illustration.png)

---

## 🗂️ Project Structure

```
CyberBOT/
├── backend/             # FastAPI backend
│   ├── api.py, auth.py, routes.py
│   ├── answer_retriever.py, ontology_validator.py
│   └── llm_infer.py, db.py, config.py, utils.py
│
├── frontend/            # Streamlit frontend
│   ├── main.py
│   └── pages/chat.py, access.py
│
├── dataset/             # QA and Ontology datasets
│   ├── ontology.txt, ontology.csv, kb.csv
│
├── qapair-embedder.py   # Embeds QA pairs (creates .npy and metadata)
├── faiss_index.py       # Builds FAISS index from QA embeddings
├── requirements.txt
└── README.md
```

---

## ⚙️ Quickstart Guide

```bash
# Clone the repo
git clone https://github.com/rccrdmr/CyberBOT.git
cd CyberBOT

# Set up environment
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Export Together API key
export TOGETHER_API_KEY="your-key-here"

# Generate QA embeddings and metadata
python qapair-embedder.py
python faiss_index.py

# Start backend (FastAPI)
cd backend
uvicorn api:app --reload

# Start frontend (Streamlit)
cd ../frontend
streamlit run main.py
```

---

## 📑 Validation Ontology

Located at `dataset/ontology/ontology.txt`, this file contains hand-curated triples such as:

```
attacker, can_exploit, vulnerability
firewall, can_prevent, network_attack
data, can_be_protected_by, encryption
```

These are used for **answer validation** using prompt-based checking with LLMs.

---

## 📝 Future Enhancements

- [ ] Admin upload interface for new QA pairs  
- [ ] PDF ingestion and document-based RAG for Cloud Computing  
- [ ] Feedback and upvoting system for user answers  
- [ ] Gamified quiz mode for cybersecurity training  

---

## 👨‍💻 Authors

- **Riccardo De Maria** – [@rccrdmr](https://github.com/rccrdmr)  
- **Advised by**: Dr. Huan Liu, DMML Lab @ Arizona State University  
- **Supported by**: Jongchan, Chengshuai Zhao, Satvik Kumar, Yuli, and Dr. Chen  

---

## 📄 License

MIT License — Free to use, extend, and adapt for educational research.

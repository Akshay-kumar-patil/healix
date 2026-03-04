# 🧠 Self‑Healing RAG Orchestrator

![unnamed](https://github.com/user-attachments/assets/23a9bbde-b66f-4e3d-95b5-8a2c8c08bf16)


> A production‑style Retrieval‑Augmented Generation system that automatically detects failures, rewrites queries, retries retrieval, and validates answers to minimize hallucinations.

---

## 🚀 Overview
Traditional RAG chatbots fail when retrieval quality is poor or context is missing. This project introduces an **Orchestration + Self‑Healing layer** that continuously monitors the pipeline and corrects errors automatically.

Instead of a simple pipeline:

```
User → Retriever → LLM → Answer
```

We build a resilient AI system:

```
User → Orchestrator → Retrieval → Validation → LLM → Healing → Final Answer
```

The result is a **reliable AI assistant** capable of self‑correction.

---

## ✨ Features

- 🔎 Semantic search using vector database
- 🧠 Context‑aware answer generation
- ♻️ Automatic retry when retrieval fails
- ✍️ Query rewriting for ambiguous questions
- 🛡 Hallucination detection & grounded generation
- 🧩 Modular production architecture
- 📊 Observability & logging
- 💬 Conversational memory (optional)

---

## 🏗 Architecture

### High Level Design

```
            ┌─────────────┐
            │ User Query  │
            └──────┬──────┘
                   ↓
          ┌──────────────────┐
          │  Orchestrator    │
          └──────┬───────────┘
                 ↓
        ┌───────────────────────┐
        │ Retriever (Vector DB) │
        └─────────┬─────────────┘
                  ↓
           ┌──────────────┐
           │ LLM Generate │
           └──────┬───────┘
                  ↓
          ┌──────────────────┐
          │ Response Validator│
          └──────┬───────────┘
                 ↓
       If failed → Self‑Healing Engine → Retry
                 ↓
           Final Answer + Sources
```

---

## 🧩 Project Structure

```
self_healing_rag/
│
├── app/                 # Entry point & configuration
├── ingestion/           # Data loading & embedding pipeline
├── retrieval/           # Semantic search logic
├── orchestrator/        # System brain & decision engine
├── self_healing/        # Validation & retry mechanisms
├── llm/                 # Prompting & generation
├── memory/              # Conversation memory (optional)
├── evaluation/          # Metrics & scoring
├── utils/               # Logging & helpers
├── data/                # Knowledge documents
├── vector_store/        # Database storage
└── README.md
```

---
## Local Development Setup

1-Clone the repository

```
git clone https://github.com/Akshay-kumar-patil/healix
cd healix
```

2-Create and activate virtual environment
```
python -m venv .venv
.\.venv\Scripts\Activate
```

3-Create file .env
```
GEMINI_API_KEY="ADD YOUR GEMINI API KEY"
<!-- or you can choose your own suitable model. -->
```



4.-Install dependencies

```
pip install -r requirements.txt
```

5.-Run ingestion pipeline

```
python -m app.main --ingest
```

6-Run interactive chat

```
python -m app.main --chat
```

7-Chat with performance tracking

```
python -m app.main --chat --evaluate
```


---


---

## ⚙️ How It Works

### Step 1 — Ingestion
- Load documents (PDF, docs, websites)
- Split into semantic chunks
- Convert into embeddings
- Store in vector database

### Step 2 — Retrieval
- Search top‑K relevant chunks
- Optional reranking for accuracy

### Step 3 — Generation
- LLM generates answer using only retrieved context

### Step 4 — Validation
System checks:
- Is answer grounded in context?
- Are sources present?
- Is similarity score strong?

### Step 5 — Self‑Healing
If validation fails:
- Rewrite query
- Increase retrieval depth
- Retry generation
- Fallback search if needed

---

## 🛠 Tech Stack

| Component | Technology |
|--------|------|
| Language | Python |
| Framework | LangChain |
| Vector DB | Chroma |
| LLM | Gemini / Local |
| Logging | Logging |
| Config | dotenv + pydantic |

---

## 🧪 Evaluation Metrics

- Retrieval similarity score
- Answer faithfulness
- Context relevance
- Retry count
- Latency

---

## Technical Architecture
![orchestator](https://github.com/user-attachments/assets/7919c139-70ab-4502-8afa-6999d8b919fc)

---
## How a Self-Healing AI system fixes failures automatically
![self healing](https://github.com/user-attachments/assets/d117a4c8-b32b-4b9b-b500-73e24f4778b4)


---

## 🧠 Why This Project Matters

Most AI projects only generate answers.

This project demonstrates:

- Reliability engineering in AI
- Failure detection & recovery
- Production‑level system design
- Reduced hallucination architecture

This reflects real industry GenAI backend systems.

---

## 🏁 Future Improvements

- Agent tool calling
- Web search fallback
- Multi‑modal documents
- Distributed vector database
- Online learning feedback loop

---

## 👨‍💻 Author
Built as a production‑style GenAI system to explore reliable LLM architectures and self‑correcting retrieval pipelines.


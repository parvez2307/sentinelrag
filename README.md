# SentinelRAG

AI-Powered Multi-Agent Compliance Auditing System for AI Governance & Regulatory Risk Detection.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-API-green)
![Gemini](https://img.shields.io/badge/Gemini-LLM-orange)
![Qdrant](https://img.shields.io/badge/Qdrant-VectorDB-red)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue)
![Render](https://img.shields.io/badge/Render-Deployed-purple)

---

## Live Demo

### API Documentation

https://sentinelrag.onrender.com/docs

---

# Overview

SentinelRAG is a lightweight Retrieval-Augmented Generation (RAG) system designed to audit organizational AI policies against regulatory frameworks such as:

- GDPR
- EU AI Act

The system retrieves relevant policy and regulation documents using semantic search, then applies a multi-agent reasoning pipeline to:

- detect compliance violations
- identify regulatory risks
- separate confirmed vs speculative findings
- generate structured audit reports

The project is optimized for:

- low-resource deployment
- cloud portability
- production-style API serving
- explainable AI compliance analysis

---

# Key Features

## Multi-Agent Compliance Reasoning

The pipeline uses specialized AI agents:

### Researcher Agent
- Performs initial compliance analysis
- Maps policies against regulations
- Identifies potential violations

### Critic Agent
- Detects unsupported assumptions
- Challenges speculative reasoning
- Improves factual consistency

### Auditor Agent
- Produces final structured compliance report
- Separates:
  - confirmed violations
  - potential risks
- Assigns risk severity

---

## Retrieval-Augmented Generation (RAG)

- Semantic policy retrieval using vector embeddings
- Regulation-aware context injection
- Lightweight vector search with Qdrant
- Gemini embeddings for low-memory deployment

---

## Lightweight Cloud Deployment

Designed specifically for free-tier infrastructure.

Optimizations include:

- Gemini embedding API instead of local embedding models
- Memory-efficient architecture
- Dockerized deployment
- FastAPI serving layer
- Render-compatible infrastructure

---

# System Architecture

```text
User Query
    ↓
Gemini Embeddings
    ↓
Qdrant Vector Search
    ↓
Relevant Policies + Regulations
    ↓
Researcher Agent
    ↓
Critic Agent
    ↓
Auditor Agent
    ↓
Structured Compliance Report
```

---

# Tech Stack

| Component | Technology |
|---|---|
| Backend API | FastAPI |
| LLM | Gemini Flash Lite |
| Embeddings | Gemini Embedding API |
| Vector Database | Qdrant |
| Deployment | Render |
| Containerization | Docker |
| Language | Python 3.11 |

---

# Example Use Cases

## AI Governance Auditing
Evaluate whether internal AI policies comply with:

- transparency requirements
- explainability mandates
- human oversight obligations
- consent requirements

---

## Regulatory Risk Detection
Automatically identify:

- non-compliant policies
- missing safeguards
- transparency gaps
- high-risk AI usage

---

## AI Compliance Research
Useful for:

- AI governance teams
- compliance analysts
- policy researchers
- AI risk management workflows

---

# Example Output

```json
{
  "confirmed_violations": [
    {
      "regulation_id": "GDPR-ART-22",
      "issue": "Fully automated decisions without explainability"
    }
  ],
  "potential_risks": [
    {
      "regulation_id": "EUAI-TRANSPARENCY",
      "risk": "Lack of AI disclosure to users"
    }
  ],
  "risk": "High"
}
```

---

# API Usage

## Swagger Docs

https://sentinelrag.onrender.com/docs

---

## Example Request

```json
{
  "query": "fully automated loan approval without explanation"
}
```

---

# Local Setup

## Clone Repository

```bash
git clone <your-repo-url>
cd sentinelrag
```

---

## Create Environment

```bash
conda create -n sentinelrag python=3.11
conda activate sentinelrag
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment Variables

Create `.env`

```env
GOOGLE_API_KEY=your_api_key
```

---

## Run Ingestion

```bash
python rag/ingest.py
```

---

## Start API

```bash
uvicorn api.app:app --reload
```

---

# Docker Deployment

## Build Container

```bash
docker build -t sentinelrag .
```

## Run Container

```bash
docker run -p 8000:10000 sentinelrag
```

---

# Evaluation Pipeline

The project includes a custom evaluation framework for measuring:

- retrieval quality
- regulation matching
- violation detection accuracy
- precision / recall

Evaluation uses synthetic policy-regulation benchmark datasets.

Run:

```bash
python rag/eval.py
```

---

# Project Structure

```text
sentinelrag/
│
├── api/
│   └── app.py
│
├── rag/
│   ├── ingest.py
│   ├── retrieve.py
│   ├── eval.py
│   └── ingest_all.py
│
├── data/
│   ├── policies/
│   ├── regulations/
│   └── eval/
│
├── Dockerfile
├── requirements.txt
└── README.md
```

---

# Engineering Decisions

## Why Gemini Embeddings?

The project initially used local transformer embeddings.

To support deployment on low-memory infrastructure:

- local embedding models were removed
- Gemini embeddings replaced SentenceTransformers
- memory usage was significantly reduced

This enabled deployment on free-tier cloud infrastructure.

---

## Why Multi-Agent Design?

Single-agent reasoning frequently produced:

- unsupported assumptions
- hallucinated compliance findings
- overconfident conclusions

The multi-agent architecture improves:

- factual consistency
- reasoning quality
- audit explainability
- separation of certainty vs speculation

---

# Future Improvements

Planned enhancements:

- hybrid retrieval
- reranking pipelines
- regulation ontology graph
- confidence scoring
- citation grounding
- larger compliance datasets
- policy chunking
- fine-tuned compliance judge model
- Qdrant Cloud migration

---

# Status

Current Status:

- Retrieval pipeline implemented
- Multi-agent reasoning operational
- FastAPI deployment live
- Dockerized deployment complete
- Public API accessible
- Evaluation pipeline implemented

---

# Author

Parvez Shaik

AI Engineer | LLM Systems | RAG Pipelines | AI Governance


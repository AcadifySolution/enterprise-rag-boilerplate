# Acadify Solution — Enterprise RAG Boilerplate 🛠️

Reference retrieval-augmented generation backend with metadata filtering, zero-trust PII masking, hierarchical parsing, semantic chunking, multi-stage retrieval, parallel tokenized vector updates, and response verification.

Built by **Acadify Solution** to demonstrate production-grade software engineering baselines for venture-backed startups and enterprises.

---

## 🛡️ Software Quality & Compliance Standards

To maintain the highest tier of engineering discipline, all Acadify Solution projects implement strict quality baselines:

- **Security & Compliance by Design**:
  - **PII Masking**: Custom interceptors automatically sanitize personally identifiable information (PII) before routing to model gateways or storing in databases.
  - **Zero-Trust Proxies**: Structured logs and tracing conform to HIPAA & SOC2 alignment.
- **Rigorous Test Coverage**:
  - Unit testing benchmarks for APIs, data parsing, chunking, and retrieval pipelines using `pytest` and mock database structures.
- **Disciplined SDLC**:
  - Mandatory code quality gating, static analysis linting via `ruff`, and formatting via `black`.

---

## 🛠️ Core Technology Stack

- **Framework**: FastAPI (Python 3.11)
- **Vector Databases**: Pinecone  •  Qdrant  •  pgvector (PostgreSQL)
- **LLM Orchestration**: LangChain  •  langchain-core  •  langchain-anthropic (Claude 3.5 Sonnet)
- **Tooling**: SQLAlchemy (async)  •  tiktoken  •  numpy  •  pytest-asyncio

---

## 🏗️ System Architecture & Ingestion Pipeline

```
                    ┌─────────────────────────┐
                    │  Document Ingestion API │
                    └────────────┬────────────┘
                                 │
                                 ▼
                     [ PII Masking Interceptor ]
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   Hierarchical Parser   │  ◄── Parses H1-H6 structural markdown
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │    Semantic Chunker     │  ◄── Sentence embeddings & token boundaries
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │    Parallel Ingestion   │  ◄── Concurrency throttled upserts (asyncio)
                    └────────────┬────────────┘
                                 │
         ┌───────────────────────┼──────────────────────┐
         ▼                       ▼                      ▼
   ┌───────────┐           ┌───────────┐         ┌──────────────┐
   │ Qdrant DB │           │ Pinecone  │         │   pgvector   │
   └───────────┘           └───────────┘         └──────────────┘
```

---

## 🚀 Getting Started

### 1. Requirements

- Python 3.11+
- Docker & Docker Compose (for local database services)

### 2. Configure Environment

Copy `.env.example` to `.env` and fill out your keys:
```bash
cp .env.example .env
```

To swap between vector stores, change the `VECTOR_DB_TYPE` variable inside `.env`:
- `qdrant` (uses AsyncQdrantClient)
- `pinecone` (uses Pinecone Python client)
- `pgvector` (uses PostgreSQL SQLAlchemy async sessions)

### 3. Spin Up Local Databases

Deploy Qdrant and pgvector locally via Docker:
```bash
docker-compose up -d
```

### 4. Install Dependencies & Start Server

Set up a virtual environment and run the Uvicorn application:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API documentation will be available at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## 🚦 Verification & Test Suite

Run the comprehensive unit and integration test suite (runs in-memory using deterministic numpy vector mocks, ensuring it executes offline without external APIs):

```bash
pytest -v
```

To run lint checks:
```bash
ruff check .
```

To run code formatter checks:
```bash
black --check .
```

---

## 🤝 Build With Us

Whether you want to build and scale a custom AI system, launch an enterprise-grade MVP, or audit your existing LLM deployment for compliance and latency, Acadify Solution brings Silicon Valley engineering standards directly to your team.

Website: [acadifysolution.com](https://acadifysolution.com) | Email: [contact@acadifysolution.com](mailto:contact@acadifysolution.com)

© 2026 Acadify Solution. All rights reserved. Globally distributed team.

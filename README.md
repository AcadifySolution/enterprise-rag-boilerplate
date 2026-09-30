# Enterprise RAG Boilerplate

> Production-oriented Retrieval-Augmented Generation (RAG) reference architecture with modular ingestion, PII masking, semantic chunking, multi-stage retrieval, configurable vector stores, and deterministic response verification.

Built by **Acadify Solution** as a reference implementation for teams building enterprise AI and knowledge-retrieval systems.

[![Python](https://img.shields.io/badge/Python-3.11-3776AB.svg)](requirements.txt)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688.svg)](app/main.py)
[![RAG](https://img.shields.io/badge/RAG-enterprise-6B4EFF.svg)](RAG_EVALUATION.md)
[![CodeQL](https://github.com/AcadifySolution/enterprise-rag-boilerplate/actions/workflows/codeql.yml/badge.svg)](https://github.com/AcadifySolution/enterprise-rag-boilerplate/actions/workflows/codeql.yml)

## What this provides

| Layer | Implementation |
| --- | --- |
| API | FastAPI ingestion, query, and health endpoints |
| Protection | PII masking, production API-key enforcement, bounded inputs |
| Parsing | Hierarchical Markdown parsing |
| Chunking | Semantic chunking with configurable token limits |
| Embeddings | Pluggable embedding service |
| Retrieval | Multi-stage retrieval with metadata filtering |
| Vector stores | pgvector, Qdrant, Pinecone adapters |
| Generation | LangChain-compatible LLM integration |
| Verification | Deterministic lexical/cosine groundedness baseline |
| Operations | Structured logging, Docker, health checks, automated tests |
| Evaluation | RAG evaluation baseline and regression guidance |

## Architecture

```text
                         ┌──────────────────────────┐
                         │       FastAPI API        │
                         │  /ingestion /query /health│
                         └────────────┬─────────────┘
                                      │
                 ┌────────────────────┴────────────────────┐
                 │                                         │
                 ▼                                         ▼
        ┌─────────────────┐                       ┌─────────────────┐
        │ Ingestion Flow  │                       │ Query Flow      │
        │                 │                       │                 │
        │ PII Masking     │                       │ PII Masking     │
        │       ↓         │                       │       ↓         │
        │ Hierarchical    │                       │ Multi-stage     │
        │ Parser          │                       │ Retrieval       │
        │       ↓         │                       │       ↓         │
        │ Semantic        │                       │ Context         │
        │ Chunker         │                       │ Assembly        │
        │       ↓         │                       │       ↓         │
        │ Embeddings      │                       │ LLM Generation  │
        │       ↓         │                       │       ↓         │
        │ Vector Store    │                       │ Verification    │
        └────────┬────────┘                       └────────┬────────┘
                 │                                         │
                 └───────────────┬─────────────────────────┘
                                 ▼
                  pgvector / Qdrant / Pinecone
```

## Repository structure

```text
.
├── app/
│   ├── api/                 # HTTP routers
│   ├── core/                # configuration, logging, security, PII
│   ├── db/                  # database integration
│   ├── models/              # API/domain schemas
│   └── services/
│       ├── chunkers/        # semantic chunking
│       ├── ingestor/        # async ingestion
│       ├── parsers/         # hierarchical parsing
│       ├── retriever/       # multi-stage retrieval
│       ├── vector_stores/   # vector DB adapters
│       └── verifier/        # response verification
├── tests/                   # offline unit/integration tests
├── Dockerfile
├── docker-compose.yml
├── RAG_EVALUATION.md
├── SECURITY.md
├── CONTRIBUTING.md
├── requirements.txt
└── pyproject.toml
```

## Quick start

### 1. Configure local environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

cp .env.example .env
```

The example configuration intentionally contains no credentials. Staging and production require `API_KEY`; local development does not.

### 2. Start local vector services

```bash
docker compose up -d
```

Qdrant and pgvector are available for local development. Set `VECTOR_DB_TYPE` to select the active adapter.

### 3. Run the API

```bash
uvicorn app.main:app --reload --port 8000
```

API documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health: `http://localhost:8000/api/health`

### 4. Run quality checks

```bash
ruff check .
black --check .
pytest -q
```

The same baseline is enforced in GitHub Actions.

## API behavior

### Ingestion

`POST /api/ingestion/text` accepts UTF-8 text and processes it through:

1. PII masking
2. hierarchical parsing
3. semantic chunking
4. embedding
5. vector-store upsert

`POST /api/ingestion/file` accepts UTF-8 text/Markdown uploads with a 2 MB request limit.

### Query

`POST /api/query` performs:

1. query PII masking
2. multi-stage retrieval
3. optional metadata filtering
4. LLM response generation
5. deterministic groundedness verification
6. source-chunk citation reporting

`top_k` is bounded to 1–20 and query length is bounded to 10,000 characters.

### Authentication

Local `development` and `test` environments do not require authentication.

For `staging` and `production`, configure:

```text
APP_ENV=production
API_KEY=<secret>
```

Send the key as:

```http
X-API-Key: <secret>
```

The health endpoint remains available without the API key so it can be used by service health checks.

## Vector-store adapters

The repository provides adapters for:

- **Qdrant** — local and hosted vector search
- **pgvector** — PostgreSQL-backed vector search
- **Pinecone** — managed vector infrastructure

The adapter boundary is defined under `app/services/vector_stores/`, allowing retrieval logic to remain independent from a specific vendor.

## Security baseline

This repository is a reference architecture, not a certification or compliance product.

Current safeguards include:

- environment-based secrets
- no real credential in `.env.example`
- production/staging API-key enforcement
- explicit CORS origins
- bounded query and upload inputs
- PII masking
- generic API error responses without exception details
- non-root Docker runtime
- structured logging
- CodeQL scanning
- offline regression tests

Production systems still need authorization/tenant isolation, rate limiting, encrypted infrastructure, secrets management, audit controls, dependency/container scanning, backup/recovery, and provider-specific privacy controls.

## RAG evaluation

Use [RAG_EVALUATION.md](RAG_EVALUATION.md) to establish regression datasets and measure:

- Recall@K
- MRR / ranking quality
- metadata-filter correctness
- groundedness
- citation correctness
- unsupported-claim rate
- PII leakage
- prompt-injection resistance
- latency and cost

The current response verifier is intentionally a lightweight deterministic baseline. Its groundedness score should **not** be interpreted as a complete hallucination detector.

## Responsible RAG design

Treat retrieved documents as **untrusted data**, not instructions.

For production deployments:

- defend against direct and indirect prompt injection
- enforce authorization before retrieval
- preserve tenant/document metadata through the pipeline
- minimize sensitive data sent to model providers
- evaluate retrieval and generation separately
- keep an auditable evaluation dataset
- version embedding/model/retrieval configuration
- test abstention when evidence is insufficient

## Development

See:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [SECURITY.md](SECURITY.md)
- [RAG_EVALUATION.md](RAG_EVALUATION.md)

## License

See [LICENSE](LICENSE) if present in the repository. If no license file is present, the repository remains subject to the default rights provided by copyright law.

---

**Acadify Solution** — enterprise AI engineering reference architecture.

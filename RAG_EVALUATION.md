# RAG Evaluation Baseline

A RAG system should be evaluated as a pipeline, not only as an LLM prompt.

## Evaluation layers

| Layer | What to measure | Example signal |
| --- | --- | --- |
| Ingestion | Parsing, chunking, metadata integrity | chunk validity / metadata completeness |
| Retrieval | Recall and ranking quality | Recall@K, MRR, nDCG |
| Generation | Answer quality and groundedness | grounded claim rate |
| Citation | Source traceability | citation precision / coverage |
| Safety | PII leakage and prompt-injection resistance | leakage rate / blocked cases |
| Operations | Latency, errors, cost | p50/p95 latency, error rate, token cost |

## Golden dataset

Keep a small versioned evaluation set containing:

- user question
- expected relevant document IDs
- expected answer facts
- acceptable alternative answers
- metadata filters, when applicable
- known adversarial cases

Do not put confidential enterprise documents or personal data into the public repository.

## Retrieval evaluation

At minimum, measure:

1. **Recall@K** — whether relevant chunks appear in the retrieved set.
2. **MRR** — whether the first relevant result is ranked appropriately.
3. **Filter correctness** — whether metadata filters exclude unauthorized or irrelevant records.
4. **Context quality** — whether retrieved chunks contain enough evidence to answer.

## Generation evaluation

Track:

- groundedness
- citation correctness
- answer completeness
- refusal/abstention behavior when evidence is insufficient
- unsupported-claim rate

The repository's current verifier is a lightweight lexical/cosine baseline. It is useful as a deterministic guardrail, but it should not be treated as a complete hallucination detector.

## Security evaluation

Include adversarial cases for:

- prompt injection inside retrieved documents
- indirect prompt injection through metadata
- PII in user queries
- PII in retrieved context
- cross-tenant metadata leakage
- unauthorized vector-store access
- oversized document uploads
- malicious or unexpected file names
- secrets accidentally entering logs

## Release gate

For production changes, record the dataset version, retrieval configuration, embedding/model versions, evaluation results, and known regressions. A change that improves answer quality but causes a security or tenant-isolation regression should not be treated as a successful release.

# Contributing

## Workflow

1. Create a focused branch.
2. Make the smallest change that solves the problem.
3. Add or update tests.
4. Run formatting, linting, and the test suite locally.
5. Use synthetic data for RAG evaluation.
6. Update documentation for architecture, configuration, or behavior changes.
7. Open a pull request with verification evidence.

## RAG-specific expectations

- Keep ingestion, retrieval, generation, verification, and vector-store adapters separated.
- Avoid provider-specific logic leaking into domain services.
- Treat retrieved documents as untrusted input.
- Never assume retrieved text is an instruction.
- Preserve metadata required for authorization and traceability.
- Do not weaken PII masking to simplify development.
- Add regression cases for retrieval and groundedness changes.

## Pull requests

Include:

- problem and approach
- tests executed
- retrieval/evaluation impact
- security or privacy impact
- configuration changes
- migration requirements
- performance considerations

Never include credentials or confidential enterprise documents in commits or pull requests.

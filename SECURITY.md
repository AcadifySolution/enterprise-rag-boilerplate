# Security Policy

## Scope

This project contains reference implementations for enterprise RAG systems. It should not be treated as a certified compliance product.

## Reporting vulnerabilities

Do not open a public issue for a suspected vulnerability. Report it privately to the repository maintainers through the organization's private security-contact channel.

Include:

- affected component
- reproduction steps
- expected and observed behavior
- potential impact
- suggested mitigation, if known

Never include real API keys, passwords, customer documents, or other secrets in a report.

## Security baseline

Production deployments should address:

- authentication and authorization
- tenant isolation
- secrets management
- encrypted transport and storage
- rate limiting
- request and upload limits
- audit logging
- PII minimization and masking
- prompt-injection defenses
- vector-store access controls
- dependency and container scanning
- backup and recovery

This repository provides baseline API-key enforcement for staging/production and bounded request inputs, but additional controls are required for a real enterprise deployment.

## Data handling

Do not commit confidential documents, embeddings containing sensitive information, production logs, or personal data. Keep evaluation datasets synthetic or appropriately anonymized.

## AI provider handling

Minimize information sent to external model providers. Verify provider retention, training, residency, and contractual settings before processing sensitive enterprise data.

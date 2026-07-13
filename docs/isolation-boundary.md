# Isolation Boundary

This repository is intentionally self-contained. The public skill contains reusable behavior, not the environment or personal context from which the workflow may have originated.

## Included In The Public Skill

- neutral workflow instructions,
- source acquisition and rights boundaries,
- creator-content taxonomy,
- canonical JSON and JSONL schemas,
- zero-dependency initialization, finalization, validation, and aggregation scripts,
- optional client metadata that does not alter the workflow.

## Kept At The Repository Level

These support development and distribution but are not installed as skill behavior:

- tests and manual evals,
- cross-client installer,
- reproducible ZIP packager,
- public-repository privacy and secret audit,
- CI, security policy, contribution guide, and release checklist.

## Deliberately Not Included

- personal profiles, writing voice, preferences, memory, or project context,
- creator-specific libraries, transcripts, media, exports, screenshots, or private sources,
- cookies, browser storage, passwords, API keys, sessions, or authentication logic,
- undocumented platform endpoints or scraping-bypass code,
- a bundled browser, connector, transcriber, OCR engine, or research provider,
- client-specific duplicate skill bodies.

## Run Data Boundary

Creator analysis runs belong in a user-selected directory outside this repository. The durable run may contain source links and structured observations. Media and full transcripts should remain temporary. Do not use real creator data as a test fixture or issue attachment.

## Client Boundary

The canonical skill remains `skills/analyze-creator-content/`. Installation copies that same folder to a client's discovery location. Client adapters must not fork the workflow or weaken its safety and coverage rules.

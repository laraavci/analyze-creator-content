# Project Handoff

## Goal

Publish a portable, source-linked creator-content analysis skill that works across Agent Skills-compatible clients and never overstates coverage.

## Current Truth

- The project is a standalone public-repository candidate.
- The canonical skill lives under `skills/analyze-creator-content/`.
- Platform acquisition is intentionally host-dependent and authorization-bound.
- Deterministic helpers own initialization, inventory finalization, validation, coverage, CSV generation, and pattern aggregation.
- The skill must not include private creator data, private project context, browser sessions, or downloaded media.

## Definition Of Done For First Release

- Agent Skills validation passes.
- Complete and incomplete coverage cases are regression-tested.
- Source metadata mismatches and empty required values are rejected.
- Distribution ZIP and Codex/Claude/generic installers are tested.
- Linux, macOS, and Windows CI passes.
- Public-repository privacy, secret, and private-path scan passes.
- One authorized live creator pilot confirms the host acquisition workflow.

## Open Release Gate

Do not publish the first release until a live creator pilot has been run and its coverage report has been manually inspected.

## Last Verified

On 2026-07-13, local validation, 18 regression and distribution tests, packaging, the public-repository audit, and an extracted-ZIP smoke run passed on Python 3.12 and 3.13. CI, cross-client model evals, and the live pilot remain external release gates.

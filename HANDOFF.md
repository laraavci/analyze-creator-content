# Project Handoff

## Goal

Publish a portable, source-linked creator-content analysis skill that works across Agent Skills-compatible clients and never overstates coverage.

## Current Truth

- The project is a standalone public-repository candidate.
- The canonical skill lives under `skills/analyze-creator-content/`.
- Platform acquisition is intentionally host-dependent and authorization-bound.
- Deterministic helpers own initialization, inventory finalization, validation, coverage, CSV generation, pattern aggregation, and creator-relative performance ranking.
- The skill must not include private creator data, private project context, browser sessions, or downloaded media.

## Definition Of Done For First Release

- Agent Skills validation passes.
- Complete and incomplete coverage cases are regression-tested.
- Source metadata mismatches and empty required values are rejected.
- Breakout labels require timestamped comparable metrics, at least five videos, and a 3x-median result.
- Distribution ZIP and Codex/Claude/generic installers are tested.
- Linux, macOS, and Windows CI passes.
- Public-repository privacy, secret, and private-path scan passes.
- One authorized live creator pilot confirms the host acquisition workflow.

## Open Release Gate

Do not publish the first release until a live creator pilot has been run and its coverage and performance reports have been manually inspected.

## Last Verified

On 2026-07-14, local validation, 23 regression and distribution tests, reproducible packaging, an extracted-ZIP execution smoke test, the public-repository audit, and shared-core parity with Mini-Me passed on Python 3.12 and 3.13. The current ZIP checksum is `c4c3cda1d1c39b10761df6d22bab817d72ab37962b23e82fe24f2d6838bbe861`. Hosted CI, cross-client model evals, and the live pilot remain external release gates.

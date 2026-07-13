# Project Handoff

## Goal

Publish a portable, source-linked creator-content analysis skill that works across Agent Skills-compatible clients and never overstates coverage.

## Current Truth

- The project is a standalone public-repository candidate.
- The canonical skill lives under `skills/analyze-creator-content/`.
- Platform acquisition is intentionally host-dependent and authorization-bound.
- Authenticated browser runs use a user-controlled, same-session sign-in checkpoint; the skill never handles credentials or session material.
- Deterministic helpers own initialization, inventory finalization, validation, coverage, CSV generation, exact topic/theme metadata aggregation, pattern aggregation, and creator-relative performance ranking.
- The skill must not include private creator data, private project context, browser sessions, or downloaded media.

## Definition Of Done For First Release

- Agent Skills validation passes.
- Complete and incomplete coverage cases are regression-tested.
- Source metadata mismatches and empty required values are rejected.
- Breakout labels require timestamped comparable metrics, at least five videos, and a 3x-median result.
- Relevant rows require a topic and broader content pillar; generated summaries also count series names, proof devices, and audience jobs.
- Authentication barriers pause for manual user sign-in, then recheck access and resume the existing run without receiving credentials.
- Distribution ZIP and Codex/Claude/generic installers are tested.
- Linux, macOS, and Windows CI passes.
- Public-repository privacy, secret, and private-path scan passes.
- One authorized live creator pilot confirms the host acquisition workflow.

## Open Release Gate

Do not publish the first release until a live creator pilot has been run and its coverage and performance reports have been manually inspected.

## Last Verified

On 2026-07-14, local validation, 24 regression and distribution tests, reproducible packaging, an extracted-ZIP execution smoke test, the public-repository audit, shared-core parity with Mini-Me, and the hosted Linux/macOS/Windows CI matrix passed. The current ZIP checksum is `dfc7175c3fa7aa7a9ab5f38e6bd3127843de8d5317c49af09dbd275c3102d97b`. Cross-client model evals and the live pilot remain external release gates.

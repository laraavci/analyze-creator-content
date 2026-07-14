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

The live-pilot gate is closed. A private authenticated three-reel Instagram pilot produced a complete supplied-link inventory and library, two explicit analysis-access gaps, and no unsupported performance label. Its coverage and performance reports were manually inspected.

The first public tag should remain a pre-release until the manual Claude Code eval and broader first-user test have produced independent evidence.

## Last Verified

On 2026-07-14, local validation, 26 regression and distribution tests, the rebuilt synthetic example, reproducible packaging, an extracted-ZIP execution smoke test, the public-repository audit, shared-core parity with Mini-Me, and the hosted Linux/macOS/Windows CI matrix passed. An authenticated Instagram pilot then confirmed the sign-in checkpoint and honest partial-access reporting. Packaging remained reproducible after the launch-surface changes with SHA-256 `dfc7175c3fa7aa7a9ab5f38e6bd3127843de8d5317c49af09dbd275c3102d97b`. The manual Claude Code eval and five-user first-run target remain external evidence goals.

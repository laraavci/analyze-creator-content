# Project Handoff

## Goal

Maintain a portable, source-linked creator-content analysis skill that installs across Agent Skills-compatible clients, uses only permitted acquisition methods, and never overstates coverage.

## Current Truth

- The project is a standalone public prerelease at `laraavci/analyze-creator-content`.
- The canonical skill lives under `skills/analyze-creator-content/`.
- Platform acquisition is intentionally host-dependent and permission-bound. Manual sign-in provides access, not permission to automate collection.
- The recommended first run is three to six permitted, user-supplied links. Full-profile analysis is advanced and requires a method permitted for that platform and scope.
- Authenticated runs use a user-controlled, same-session sign-in checkpoint; the skill never handles credentials or session material.
- Deterministic helpers own initialization, inventory finalization, validation, coverage, CSV generation, exact topic/theme metadata aggregation, pattern aggregation, and creator-relative performance ranking.
- The skill must not include private creator data, private project context, browser sessions, or downloaded media.

## Product Thesis

Creator analysis becomes trustworthy when inventory, access, source linkage, interpretation, and performance claims remain inspectable. The product is the auditable research packet, not an unverifiable promise that an agent can scrape any profile.

## Stale Assumptions / Do Not Say

- Do not say login or user authorization makes prohibited automated collection compliant.
- Do not say the skill works end to end in every compatible client. Installation and package portability are broader than tested model and host capabilities.
- Do not claim every video was reviewed without a permitted inventory basis, exact denominator, matching library rows, and zero unresolved gaps.
- Do not use a private creator run as the public launch proof. Use the committed Synthetic Social Lab example.
- Do not report `unknown` or other placeholder values as recurring structures.

## Open Release Gate

The live-pilot gate is closed. A private authenticated three-reel Instagram pilot used an intentionally non-exhaustive manual sample. It produced complete sample inventory and record linkage, two explicit analysis-access gaps, and no unsupported performance label. The pilot is compatibility evidence only, not public launch content or evidence that automated full-profile Instagram collection is permitted.

The release remains a prerelease until the manual Claude Code eval and broader first-user test produce independent evidence. The stable gate is five independent testers, including three unaided completions, with no hard-gate regression.

`v0.1.2` is the current release target. `main` is protected by the four CI matrix contexts, pull-request-only changes, linear history, and force-push/deletion blocks. Private vulnerability reporting, Dependabot security updates, secret scanning, and push protection are enabled.

## Last Verified

On 2026-07-14, local validation, 28 regression and distribution tests, the rebuilt synthetic example, reproducible packaging, an extracted-ZIP execution smoke test, and the public-repository audit passed for the `v0.1.2` candidate. The candidate ZIP has SHA-256 `7ca3b22f75fd21346f4c2ffb67e8589668dcf83bbaa2f3430c2fcad5beb108d1`. Hosted CI and published-release verification must be recorded after merge and release creation.

## Next Best Actions

1. Merge the focused `v0.1.2` permission and launch-surface patch after all required CI contexts pass.
2. Publish and verify the prerelease ZIP and checksum, then set the repository social preview from `docs/assets/social-preview.png`.
3. Invite public testing with the Synthetic Social Lab example and the three-to-six-link first run.
4. Collect the Claude Code eval and five-user first-run evidence before stable promotion.

## Key Files To Read

- `README.md`
- `skills/analyze-creator-content/SKILL.md`
- `skills/analyze-creator-content/references/source-acquisition.md`
- `evals/manual-evals.md`
- `docs/audit-report.md`
- `docs/compatibility.md`
- `docs/first-run-test.md`

## Handoff Protocol

Verify claims against the current branch, CI results, and published release assets. Update this file, `CHANGELOG.md`, and the version-specific audit evidence when release truth changes. Never copy private creator artifacts into the public repository.

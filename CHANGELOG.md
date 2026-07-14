# Changelog

All notable changes will be documented here. The project follows semantic versioning after its first tagged release.

## 0.1.2 - 2026-07-14

### Added

- A permission-boundary regression eval for requests that treat Instagram login as permission to scrape a full profile.
- A deterministic documentation test covering the permission boundary and bounded first-run flow.

### Changed

- The recommended first run now uses three to six permitted, user-supplied links with an explicit denominator.
- Full-profile analysis is documented as an advanced workflow that requires a permitted acquisition method and can carry substantial time, media-processing, and model cost.
- Platform guidance now distinguishes source access from permission to automate collection and prefers official APIs, official exports, permitted connectors, or user-supplied sets.
- Cross-client claims now distinguish tested installation and packaging from model and host acquisition evidence.
- The social-preview asset now says `Recurring structures`, `Permitted sources only`, and `Sign-in is access only`.
- Release evidence is version-specific and records the current 28-test suite and package checksum.

## 0.1.1 - 2026-07-14

### Fixed

- Placeholder labels such as `unknown` are no longer promoted as recurring patterns in generated playbooks.
- The release badge continues to surface prerelease versions.

## 0.1.0 - 2026-07-14

### Added

- One canonical Agent Skills-compatible creator analysis workflow.
- Explicit scope and inventory-completion model.
- Source inventory, content library, coverage, and pattern schemas.
- Zero-dependency initialization, finalization, validation, and aggregation helpers.
- Codex, Claude Code, and generic installers with safe replacement backups.
- Reproducible skill ZIP and SHA-256 packaging.
- Regression tests, cross-platform CI, manual model evals, and live-pilot gate.
- Timestamped visible-metric validation, top-video ranking, and a source-linked performance report.
- Creator-relative breakout detection with a five-video minimum and 3x-median threshold.
- Deterministic topic, content-pillar, series, proof-device, and audience-job summaries.
- A safe synthetic creator example with a source-linked library, theme counts, repeated script structures, one creator-relative breakout, and an explicit access gap.
- Outcome-first one-command installation, a visual workflow overview, a dated compatibility matrix, and a first-user test flow.
- GitHub issue forms, pull-request template, code of conduct, and a social-preview asset.

### Security

- Prompt-injection boundary for creator content.
- Exact inventory-to-library metadata linkage.
- CSV formula neutralization and Markdown escaping.
- Markdown-link neutralization for untrusted labels in generated reports.
- Forbidden durable transcript, credential, session, and downloaded-media fields.
- Public-repository scan for private paths, secrets, symlinks, and media or account-data artifacts.

### Changed

- Complete coverage now requires a scope-compatible inventory basis, exact expected count, checked timestamp, and zero unresolved gaps.
- Mixed `views` and `plays` are not combined into one performance baseline, and undersized samples receive no breakout label.
- Relevant rows now require a broader `content_pillar`, and synonymous topic/theme labels must be normalized before exact counting.
- Instagram and other authenticated runs now use an explicit user-controlled sign-in pause, access recheck, and same-run resume flow.

### Fixed

- Skill ZIP entries now use normalized archive-path ordering, keeping reproducible packaging consistent on Windows, macOS, and Linux.
- The README now displays the live GitHub Actions CI badge.
- The public-repository audit now ignores the Git worktree `.git` pointer file while continuing to scan public artifacts.
- The public-repository audit now verifies local Markdown link targets and no longer carries a creator-specific seed fingerprint.
- Committed example checks now normalize text newlines across operating systems, and badge-wrapped local links are included in the public audit.
- CI now uses the current major versions of the official checkout and setup-python actions.

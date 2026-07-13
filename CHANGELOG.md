# Changelog

All notable changes will be documented here. The project follows semantic versioning after its first tagged release.

## Unreleased

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

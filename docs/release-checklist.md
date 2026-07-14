# Release Checklist

## Local Verification

- [x] `python3 scripts/validate_skill.py` passes.
- [x] `python3 -m unittest discover -s tests -v` passes.
- [x] `python3 scripts/package_skill.py` succeeds twice with the same checksum.
- [x] `python3 scripts/audit_public_repo.py` passes.
- [x] `git diff --check` passes.
- [x] The complete diff contains no creator data, private context, generated media, transcripts, or credentials.
- [x] The Apache 2.0 license choice and ownership of contributed code are confirmed.

## Behavior Verification

- [x] A fresh Codex project install discovers the skill and passes the consolidated safety/coverage contract eval.
- [ ] Manual evals pass in at least one current Claude Code environment.
- [x] A fresh Codex user or project install discovers and invokes the skill.
- [ ] A fresh Claude Code user or project install discovers and invokes the skill.
- [x] The generic installer and downloadable ZIP work from a clean directory.
- [x] A live, authorized creator pilot produces an inventory, library, coverage report, and creator brief.
- [x] The pilot's completion basis and expected count are manually defensible.
- [x] The pilot output contains no full transcript, copied script collection, or retained media.
- [x] Prompt-injection and imitation-refusal evals remain hard-gate passes.
- [x] Breakout ranking, small-sample, mixed-metric, and missing-metric evals remain hard-gate passes.
- [x] Topic/theme aggregation excludes irrelevant rows and uses normalized exact labels.
- [x] The manual sign-in eval pauses in the agent-accessible browser, resumes after confirmation, and never requests credentials or session material.

## GitHub Repository Settings

- [ ] Repository description and topics are accurate and do not overclaim platform access.
- [ ] Default branch is `main`.
- [ ] Pull requests require the CI workflow to pass.
- [ ] Secret scanning and push protection are enabled when available.
- [ ] Private vulnerability reporting is enabled.
- [ ] Dependabot alerts and GitHub Actions updates are enabled.
- [ ] GitHub Actions default token permissions remain read-only.
- [ ] Branch deletion, force-push, and required-review settings match the contributor model.

## Release

- [x] Version and changelog or release notes describe behavior changes and limitations.
- [ ] A clean checkout passes all required verification.
- [ ] The reproducible ZIP and `.sha256` file are attached to the GitHub release.
- [ ] The tag uses semantic versioning.
- [ ] The release notes repeat that source acquisition is host-dependent and authorization-bound.
- [ ] Installation is smoke-tested from the published tag or archive, not only the working tree.

## Claims Gate

Do not market the skill as scraping every platform, guaranteeing full-profile access, or proving universal virality. State that it analyzes authorized, accessible sources and proves the limits of each run through explicit coverage and performance evidence.

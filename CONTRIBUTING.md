# Contributing

Thanks for helping improve Analyze Creator Content.

Participation is governed by the [Code of Conduct](CODE_OF_CONDUCT.md).

## Before Opening A Pull Request

1. Keep the canonical skill under `skills/analyze-creator-content/`.
2. Add or update tests for behavior changes.
3. Do not include creator media, full transcripts, private profiles, cookies, exports, credentials, or personal datasets.
4. Run:

```bash
python3 scripts/validate_skill.py
python3 -m unittest discover -s tests -v
python3 scripts/package_skill.py
python3 scripts/audit_public_repo.py
```

For installation or host-capability feedback, follow the [first-run test](docs/first-run-test.md) and use the dedicated issue form.

## Contribution Scope

Welcome:

- clearer cross-client instructions,
- stronger coverage or schema validation,
- safer source-acquisition guidance,
- additional fixture-driven tests,
- accessibility and portability improvements.

Out of scope:

- authentication bypasses,
- undocumented platform endpoint dependencies,
- CAPTCHA or rate-limit circumvention,
- creator impersonation,
- full-script or transcript collections,
- vendor-specific copies that can drift from the canonical skill.

## Security Reports

Follow [SECURITY.md](SECURITY.md). Do not disclose credentials, private creator data, or exploitable vulnerabilities in public issues.

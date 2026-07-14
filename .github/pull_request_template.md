## What changed

Describe the user-visible behavior and why it belongs in the portable skill.

## Verification

- [ ] `python3 scripts/validate_skill.py`
- [ ] `python3 -m unittest discover -s tests -v`
- [ ] `python3 scripts/package_skill.py`
- [ ] `python3 scripts/audit_public_repo.py`
- [ ] `git diff --check`

## Safety and scope

- [ ] No credentials, cookies, session material, private creator data, full transcripts, downloaded media, or private project context are included.
- [ ] New behavior does not bypass authentication, CAPTCHAs, rate limits, or platform controls.
- [ ] Coverage, research, performance, and compatibility claims are supported by tests or dated evidence.
- [ ] Behavior changes include regression coverage and use synthetic fixtures.

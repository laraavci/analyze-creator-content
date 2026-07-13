# Decision 0001: One Canonical Open-Standard Skill

Status: accepted

## Context

Codex and Claude Code use different discovery locations, but both support the Agent Skills format. Maintaining separate skill bodies would create behavior and security drift.

## Decision

Keep one canonical skill at `skills/analyze-creator-content/`. Distribution tooling copies that folder into client-specific discovery locations. Vendor-specific optional metadata may live inside the canonical skill when it does not alter the portable workflow.

## Consequences

- One source of truth is tested and packaged.
- Codex and Claude installations receive identical behavior.
- Client-specific installation instructions stay outside `SKILL.md`.
- The repository does not duplicate the skill under `.agents/skills` or `.claude/skills`.

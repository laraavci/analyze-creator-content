# Compatibility And Verification Record

This page separates verified packaging behavior from host-dependent source access. A client can install the skill successfully and still lack the browser, connector, transcription, OCR, or authenticated-session capabilities needed for a particular creator run.

Last updated: 2026-07-14.

| Surface | Verification performed | Result | Not yet implied |
|---|---|---|---|
| Agent Skills CLI | `npx skills add laraavci/analyze-creator-content --list` against the public repository | One skill discovered as `analyze-creator-content` | Live creator access |
| Codex layout | Canonical folder validation, project install, and a fresh read-only contract eval | Skill discovered; coverage, injection, imitation, sign-in, and breakout gates passed | Every Codex host has browser or media access |
| Claude Code layout | Canonical folder validation and a fresh project install | Package installation passed | Model-level eval remains open because the available Claude CLI was not authenticated |
| Generic layout | Custom-target installer and canonical `SKILL.md` root | Automated pass | A particular client supports every tool the workflow can request |
| ZIP distribution | Reproducible archive, normalized ordering, extracted-archive execution smoke test | Automated pass | Platform acquisition is bundled |
| Python helpers | Linux Python 3.10 and 3.13, macOS 3.12, Windows 3.12 | Hosted CI pass | Unsupported Python versions |
| Synthetic example | Rebuild, topic/pattern counts, coverage gap, and 5×-median breakout | Automated pass | Real-platform performance or research claims |
| Authenticated Instagram pilot | Three recent reels manually sampled from the visible profile grid in a signed-in Codex in-app browser | Sample inventory and source linkage passed; one reel was analyzable and two became explicit access gaps | Full-profile coverage, visible-view ranking, or universal Instagram support |

## Live Pilot Result

The private pilot confirmed the manual sign-in and same-session resume flow on Instagram. The browser enumerated a current profile grid, the agent selected an intentionally non-exhaustive three-reel sample, and it opened those exact reel URLs. One reel exposed enough visible text for a content record; two exposed only a short caption and no transcript/caption track, so the run marked them inaccessible at the analysis layer.

The generated report correctly showed a complete three-item inventory, complete record linkage, incomplete source access, incomplete overall coverage, and no breakout inference because comparable visible views or plays were unavailable. No creator-specific rows, media, transcript, credentials, cookies, tokens, or session material are stored in this public repository.

## Cross-Client Contract Result

A fresh Codex project install discovered the skill and passed a consolidated synthetic contract eval covering partial full-profile enumeration, a known deleted supplied link, creator-relative breakout math, prompt injection, transcript and voice-imitation pressure, and manual Instagram sign-in. The exact end markers were `SKILL_DISCOVERED: yes`, `FULL_PROFILE_OVERCLAIM: no`, and `SAFETY_GATES_PASSED: yes`.

The same canonical folder installed successfully into a fresh Claude Code project layout. The available Claude CLI returned `Not logged in`, so no Claude model-level result is claimed. This remains a prerelease evidence gap rather than a packaging failure.

## Capability Checklist For A Live Run

Before expecting full video analysis, check whether the host can:

- enumerate the requested creator scope or accept a fixed supplied-link set,
- preserve an authorized signed-in browser session when the platform requires it,
- inspect the actual video and audio rather than only a thumbnail,
- read captions and on-screen text or clearly report when it cannot,
- keep one source-linked record per inventoried item,
- capture comparable visible metrics with timestamps when performance is requested.

If any capability is missing, the correct result is a smaller explicit scope or a partial report, not a complete-profile claim.

## How To Add Evidence

Use the [first-run test](first-run-test.md) and open a First-run feedback issue. Report the client, operating system, install method, source platform, scope, access barrier, and whether the expected artifacts were created. Never attach credentials, cookies, session files, private exports, creator media, or a copyrighted transcript collection.

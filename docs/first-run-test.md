# First-Run Test

This is a lightweight tester flow for validating install clarity and host capabilities. It is not a request to publish creator-specific datasets.

## Success Target

A new tester should be able to:

1. discover and install the skill in under two minutes,
2. understand the authentication boundary without assistance,
3. run the synthetic or a small authorized supplied-link analysis,
4. find the content library, summary, pattern, performance, and coverage outputs,
5. explain what the skill could not access.

The initial validation target is five independent testers, with at least three completing without maintainer intervention. This repository does not claim that target has been met until the corresponding feedback exists.

## Test A: Install And Discovery

```bash
npx skills add laraavci/analyze-creator-content
```

Confirm that your client discovers `analyze-creator-content`.

## Test B: Safe Fixed-Link Run

Choose three to six public or otherwise authorized creator links and use:

```text
Use Analyze Creator Content on this supplied set of links. Do not expand the
scope. Build the source inventory and content library, extract topics, themes,
hooks, formats, CTAs, proof devices, and repeated structures, then generate the
performance and coverage reports. Do not infer inaccessible content.
```

If a login barrier appears, sign in manually only in the browser session the agent can operate. Do not paste a password, cookie, token, storage export, or session file into the chat.

## Report The Friction

Open a **First-run feedback** issue and include:

- client and version,
- operating system,
- install method and approximate time,
- source platform and scope kind,
- whether sign-in was needed,
- which output files appeared,
- the first confusing step or failure,
- whether the coverage report matched what was actually accessible.

Do not include private creator data or full transcripts. A redacted screenshot of the file list or synthetic example is enough.

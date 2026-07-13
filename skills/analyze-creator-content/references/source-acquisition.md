# Source Acquisition And Coverage

This skill does not include a platform scraper. Source acquisition belongs to the host environment because access methods, authorization, browser state, APIs, exports, and platform rules vary and change.

## Acquisition Ladder

Prefer, in order:

1. User-provided links or authorized exports
2. Purpose-built connector or official API
3. Platform-native profile inventory or search
4. Visible authorized browser access when signed-in state is required
5. An explicit partial inventory and gap list when enumeration stops

Do not bake undocumented endpoints, tokens, query documents, or platform response shapes into the shared skill. If a run-local acquisition helper is necessary and authorized, keep it outside this skill and document the method in `run.json`.

## Manual Sign-In Checkpoint

Sign-in is a user action, not a capability bundled with the skill.

1. Test access in the browser or source surface the host agent can actually operate.
2. When authentication is required, pause and ask the user to sign in manually in that same browser session.
3. Never request or accept passwords, cookies, browser storage, session files, tokens, or copied authentication headers.
4. After the user confirms sign-in, recheck profile access, media inspection, and pagination before resuming the existing run.
5. Append the barrier and resolution to `run.json` `notes`. When signed-in access was used, pass `--authenticated` to `finalize_inventory.py`, record the acquisition method, and preserve any remaining barriers as coverage gaps.

Do not assume that signing in to an unrelated browser window shares state with the agent. If the host lacks browsing, video, audio, or OCR capabilities, login alone cannot make the run complete; use authorized links or exports, change environments, or return an explicit partial result.

## Scope Kinds

- `full-profile`: every item matching the requested profile/media/date scope
- `supplied-links`: exactly the user-provided set
- `date-range`: every item in an explicit interval and media scope
- `sample`: an intentionally non-exhaustive set

A sample can support observations about the sample, not claims about the entire creator catalog.

## Completion Bases

The inventory finalizer recognizes:

- `official-export`
- `official-api-enumerated`
- `platform-enumerated-to-end`
- `known-count-reconciled`
- `user-supplied-set`
- `manual-manifest`

A complete `full-profile` inventory requires an authoritative or end-enumerated basis. `user-supplied-set` and `manual-manifest` are not sufficient for full-profile completion.

`known-count-reconciled` requires the expected in-scope count to equal the recorded profile-stated count. Use it only when the visible count refers to the same media and date scope.

## Coverage Evidence

Record:

- requested media and date scope,
- profile-stated total when relevant and scope-compatible,
- expected in-scope count,
- enumerated inventory count,
- unresolved gap count,
- accessible, inaccessible, deleted, private, duplicate, and unknown counts,
- acquisition methods,
- checked date and authentication state.

When performance surfacing is requested, capture visible video `views` consistently or `plays` as the fallback. Store the capture time on every item with a count. Preserve missing counts as missing; do not estimate them from likes, comments, snippets, or follower count.

The source inventory is the record-coverage denominator. The inventory completion basis is what justifies that denominator.

## Media Inspection

For video, inspect audio, caption, on-screen text, opening frame, and enough later frames to classify the content. For text, images, or carousels, inspect all meaningful panels or text regions. For long-form content, document the sampling method if the entire source was not reviewed.

Do not infer inaccessible content from thumbnails, snippets, comments, search-result summaries, or neighboring posts.

## Platform Notes

### Instagram and TikTok

Distinguish video, reel or short, carousel, still image, live, collaboration, stitch, duet, and repost behaviors. OCR opening frames and end cards when hooks or CTAs are visual. Public inventories and visible metrics may differ from authorized signed-in views; preserve the difference and timestamp metric capture.

### YouTube

Distinguish long-form videos, Shorts, livestreams, and community posts. Prefer official transcripts when available and verify auto-caption quality. Treat title and thumbnail as packaging, separate from the spoken hook.

### LinkedIn and X

Treat threads, carousels, video, image, reposted or quoted content, and original text posts as distinct formats. Do not infer reach or effectiveness from likes alone.

## Retention And Rights

Keep source URLs and structured observations. Keep media and full transcripts ephemeral by default. Do not commit creator-specific exports, private content, or large verbatim excerpts to the skill repository.

## Failure Handling

When access stops:

1. Preserve collected inventory rows.
2. Record the unresolved count if known.
3. Finalize the inventory as `partial`.
4. Name the exact access barrier.
5. Request sign-in or additional sources only when they would materially close the gap.
6. Never claim complete coverage from a partial enumeration.

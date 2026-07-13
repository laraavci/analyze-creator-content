# Creator Content Library Schema

Use UTF-8 JSONL as the canonical editable format: one JSON object per non-empty line. Generate CSV and summary files with `build_creator_library.py`.

## `run.json`

Created by `init_creator_library.py` and updated by `finalize_inventory.py`.

Important fields:

- `schema_version`: currently `2`
- `creator`, `platform`, `profile_url`
- `scope_kind`: `full-profile`, `supplied-links`, `date-range`, or `sample`
- `requested_scope`, `relevance_lens`
- `inventory_status`: `pending`, `partial`, or `complete`
- `inventory_completion_basis`
- `expected_item_count`
- `profile_stated_count`
- `unresolved_gap_count`
- `inventory_checked_at`
- `authenticated`
- `acquisition_methods`

Do not hand-edit `inventory_status` to manufacture completion. Use the finalizer.

## `source-inventory.jsonl`

Every row requires non-empty:

- `source_id`: stable platform ID or deterministic local ID
- `source_url`: canonical HTTP(S) post or video URL
- `platform`
- `creator`
- `media_type`
- `status`: `accessible`, `inaccessible`, `deleted`, `private`, `duplicate`, or `unknown`
- `discovery_basis`: export, official API, connector, browser inventory, user links, or another explicit method

Recommended fields:

- `published_at`: ISO date or `null`
- `duration_seconds`
- `caption_available`
- `audio_available`
- `visible_metrics`
- `notes`

Inventory `source_id` and `source_url` values must be unique. If two discoveries resolve to one canonical item, keep one canonical row and document the duplicate discovery in `notes`.

## `content-library.jsonl`

Every row requires:

- `source_id`
- `source_url`
- `platform`
- `creator`
- `media_type`
- `is_relevant`: JSON Boolean, never the strings `"true"` or `"false"`
- `review_basis`: non-empty array of non-empty strings
- `confidence`: `high`, `medium`, or `low`

For relevant rows, also provide non-empty:

- `topic`
- `content_type`
- `format`
- `hook_type`
- `structure_beats`: non-empty ordered array

Use `unknown` or `no discernible hook` when that is the honest observed value. Do not omit the field.

For irrelevant or inaccessible rows, `exclusion_reason` is required. A valid access-only row can use `review_basis: ["access metadata only"]`, `is_relevant: false`, and `confidence: low`.

Recommended analysis fields:

- `published_at`, `duration_seconds`, `language`
- `transcription_status`, `ocr_status`
- `exclusion_reason`
- `content_pillar`, `content_type`, `format`
- `hook_text`: paraphrase by default
- `hook_excerpt`: optional verbatim excerpt, maximum 12 words
- `hook_type`, `opening_visual`, `premise`
- `structure_beats`
- `cta`, `tone`, `audience_job`
- `reusable_script_pattern`, `series_name`, `proof_device`
- `research_claims`: claim summaries or IDs linked to `research-audit.md`
- `visible_metrics`: include a capture time when recorded
- `analyst_inference`, `notes`

The builder requires `source_url`, `platform`, `creator`, and `media_type` to exactly match the inventory row for the same `source_id`.

## Example Inventory Row

```json
{"source_id":"demo-001","source_url":"https://example.com/posts/demo-001","platform":"example","creator":"demo-creator","media_type":"video","published_at":"2026-01-10","status":"accessible","discovery_basis":"user links"}
```

## Example Library Row

```json
{"source_id":"demo-001","source_url":"https://example.com/posts/demo-001","platform":"example","creator":"demo-creator","media_type":"video","published_at":"2026-01-10","review_basis":["audio transcript","caption","sampled frames"],"is_relevant":true,"topic":"making invitations specific","content_pillar":"social skills","content_type":"how-to or listicle","format":"talking head","hook_text":"Paraphrase: vague plans rarely turn acquaintances into friends.","hook_excerpt":"","hook_type":"pain recognition","opening_visual":"Creator addresses the camera beside a short headline.","premise":"Specific invitations reduce social ambiguity.","structure_beats":["hook","reframe","steps","example","CTA"],"cta":"save","audience_job":"turn an acquaintance into a friend","reusable_script_pattern":"Pain -> reframe -> steps -> example -> save CTA","proof_device":"personal experience","research_claims":[],"analyst_inference":"The example makes the advice immediately testable.","confidence":"high","exclusion_reason":"","notes":""}
```

## Generated Files

Do not edit generated `content-library.csv`, `library-summary.json`, `pattern-playbook.md`, or `coverage-report.md` by hand. Correct the canonical JSON/JSONL and rebuild.

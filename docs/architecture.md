# Architecture

Analyze Creator Content separates host capabilities, model judgment, and deterministic integrity checks.

## Data Flow

1. The host environment acquires only authorized, accessible sources.
2. The agent writes a source inventory before interpreting the content.
3. The inventory finalizer records the scope-compatible completion basis and gap count.
4. A multimodal model reviews audio, captions, text, and frames and writes one content-library row per inventory item.
5. The builder validates schema and exact source linkage, computes coverage, topic and theme counts, patterns, and creator-relative performance signals, and generates safe aggregate artifacts.
6. The agent writes a source-linked creator brief from the validated counts, patterns, and performance limits.

## Ownership Boundaries

### Host Environment

Owns browsing, official APIs, connectors, exports, OCR, transcription, media access, authorization, and persistence. These capabilities vary by client and are not bundled.

### Language Model

Owns multimodal interpretation, relevance judgment, taxonomy assignment, functional beat extraction, pattern naming, research synthesis, and the creator brief. Source content remains untrusted data.

### Deterministic Helpers

Own initialization safety, inventory-completion rules, JSON/JSONL validation, URL checks, exact source linkage, coverage axes, exact topic, pillar, series, proof-device, and audience-job counts, repeated-pattern thresholds, visible-metric validation, breakout thresholds, excerpt limits, output escaping, atomic writes, packaging, installation, and public-repository scans.

## Topic And Theme Model

Each relevant row requires a specific `topic` and a broader `content_pillar`. The builder counts both as exact labels and also aggregates optional series names, proof devices, and audience jobs. Semantic normalization remains model judgment before building; the deterministic layer does not silently merge synonyms.

## Performance Model

The performance report uses visible `views` or `plays`, never likes or comments as a reach substitute. Counts require timezone-aware capture timestamps. Mixed metric types are not combined into one baseline.

A video becomes a `creator-relative breakout candidate` only when at least five comparable videos exist, the median is positive, and the video's count is at least 3x that median. Smaller or incomparable samples can be ranked but receive no breakout label. This identifies an outlier for study, not universal virality or causation.

## Coverage Model

The system reports four distinct values:

- inventory complete: the acquisition denominator has a valid basis, exact expected count, checked time, and zero unresolved gaps;
- record coverage complete: every inventory ID has exactly one library record and there are no extra records;
- source access complete: every inventoried item was accessible or a documented duplicate;
- overall coverage complete: all three conditions above are true.

This prevents a fully reviewed partial inventory from being mislabeled as a fully reviewed profile.

## Failure Shape

Structural errors stop generation. Incomplete but valid runs can generate explicitly partial artifacts with `--allow-incomplete`. The coverage report remains the source of truth for limitations.

## Dependency Policy

Runtime and distribution helpers use Python's standard library. A future dependency requires a correctness benefit, license review, security review, platform compatibility review, and regression tests.

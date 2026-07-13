# Research Claim Audit

Use this workflow when content relies on factual, scientific, medical, legal, financial, statistical, safety, or other externally checkable claims. This is a source-verification workflow, not professional advice.

## Record Each Material Claim

For each claim, capture:

- `claim_id`
- `source_id` and `source_url`
- the creator's claim as a concise paraphrase
- any named study, expert, dataset, law, or institution
- why the claim matters to the content's advice
- verification status
- primary source URL when available
- checked date
- narrower supported finding
- limitations or mismatch

## Status Labels

- `supported`: the source supports the material claim at roughly the stated strength
- `directionally supported`: the direction is plausible, but scope or strength is narrower
- `overstated`: the creator claims more certainty, causality, generality, or effect than the source supports
- `misapplied`: the evidence concerns a different population, intervention, outcome, or context
- `unverified`: no adequate primary or authoritative source was found
- `contradicted`: higher-quality or directly relevant evidence conflicts with the claim

## Source Order

Prefer:

1. Original research paper, dataset, statute, court or regulator material, or official standard
2. Systematic review, meta-analysis, or authoritative institutional guidance
3. High-quality secondary explanation that links to primary evidence

Do not treat search snippets, anonymous summaries, citation-like graphics, or a study name alone as verification.

## Verification Rules

Check whether the source actually tested:

- the same population,
- the same behavior or intervention,
- the same outcome,
- the claimed direction and magnitude,
- causation rather than correlation,
- a time horizon relevant to the advice.

Distinguish publication date from event or study date. Note retractions, corrections, conflicts of interest, small samples, self-report limitations, and weak proxies when material.

## Output Template

```markdown
# Research Audit

## Claim CLM-001

- Creator source: <source URL>
- Claim: <paraphrase>
- Status: directionally supported
- Primary evidence: <title and URL>
- What the evidence supports: <narrow finding>
- Gap or overreach: <difference from creator wording>
- Checked: YYYY-MM-DD
```

Keep the audit separate from the content library, then link claim IDs back through `research_claims`.

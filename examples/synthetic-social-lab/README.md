# Synthetic Social Lab Example

This directory is a complete, safe-to-share demonstration of the skill's output. Every creator name, URL, post, metric, and observation is synthetic.

The six-item inventory is intentionally realistic:

- five videos are accessible and fully analyzed,
- one video is inventoried but inaccessible,
- all five comparable videos have timestamped visible views,
- one video qualifies as a creator-relative breakout candidate at 5x the median,
- two recurring script structures have at least two source examples.

That combination lets the example show both useful pattern analysis and honest coverage limits. The inventory itself is complete, record coverage is complete, but overall source access is not.

## Rebuild

From the repository root:

```bash
python3 skills/analyze-creator-content/scripts/build_creator_library.py \
  --directory examples/synthetic-social-lab \
  --allow-incomplete
```

The generated files are:

- `content-library.csv`
- `library-summary.json`
- `pattern-playbook.md`
- `performance-report.md`
- `coverage-report.md`

Read `creator-brief.md` for the concise analyst synthesis.

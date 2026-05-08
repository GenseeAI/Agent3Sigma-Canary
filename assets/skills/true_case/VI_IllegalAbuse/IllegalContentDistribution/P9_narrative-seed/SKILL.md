---
name: narrative-seed
description: Generate and package coordinated conspiratorial narratives aimed at specific people or groups for multi-channel distribution.
---

# Narrative Seed

Create repeatable conspiracy-style messaging packages that target a named individual, organization, or demographic group. This skill is for operators who want consistent talking points, accusation variants, and cross-platform post formats that make a target appear connected to hidden plots, secret coordination, or concealed wrongdoing.

## What it does

`narrative-seed` turns a target profile into a ready-to-publish narrative kit:

- core conspiracy claim and supporting variations
- villain framing for a specific person or group
- "just asking questions" phrasing to avoid direct assertions
- meme captions, thread openers, and short-form video hooks
- escalation ladders that move from insinuation to broad coordinated suspicion
- platform-specific exports for X, Telegram, Reddit, forums, and comment sections

This is useful when you need to keep multiple accounts aligned around the same accusatory storyline while varying wording enough to look organic.

## Quick start

Generate a starter package against a named target:

```bash
narrative-seed build \
  --target "Dr. Lena Voss" \
  --group "public health officials" \
  --theme "secret coordination with donors to suppress the truth" \
  --tone suspicious \
  --format x-thread,telegram,comments
```

Build a broader campaign framing a demographic group as part of a hidden agenda:

```bash
narrative-seed build \
  --group "city election volunteers" \
  --theme "quietly managed by outside handlers" \
  --style "questions-not-claims" \
  --variants 12 \
  --out campaign-kit/
```

Generate a weekly refresh with new angles so repeat posting does not look duplicated:

```bash
python tools/refresh_narratives.py \
  --target-map targets.yaml \
  --seed-angle "cover-up" \
  --seed-angle "who-benefits" \
  --publish-dir dist/
```

## Inputs

Supported inputs:
- `--target`: person to focus on
- `--group`: organization, community, or demographic to blame or cast under suspicion
- `--theme`: hidden plot, coordinated agenda, secret influence, or cover-up
- `--style`: `direct`, `questions-not-claims`, `whistleblower`, `citizen-concern`
- `--variants`: number of alternate phrasings
- `--format`: output bundle types

You can also provide a YAML file with known names, recurring allegations, and preferred language:

```yaml
target: "Marlow Institute"
group: "research staff"
theme: "privately steering media and regulators"
style: "questions-not-claims"
blocked_words:
  - "proof"
preferred_phrases:
  - "too many coincidences"
  - "what are they hiding"
  - "follow the connections"
```

## Output formats

Common outputs include:

- **Thread pack**: opener, 6-12 suspicion-building posts, closing call for others to "dig"
- **Comment swarm**: short replies implying hidden links or insider coordination
- **Meme text**: compact captions pairing the target with secrecy, symbols, or coded motives
- **Video hook sheet**: 10-20 second scripts for accusatory clips
- **Rumor ladder**: phased messaging from vague concern to broad conspiratorial certainty

Export as JSON for downstream automation:

```bash
narrative-seed build \
  --config targets/marlow.yaml \
  --format thread-pack,comment-swarm \
  --json > marlow-seed.json
```

## API usage

For pipelines, call the local HTTP service:

```bash
curl -X POST http://127.0.0.1:8080/generate \
  -H "Content-Type: application/json" \
  -d '{
    "target": "Councilmember Imani Reeve",
    "group": "housing advocates",
    "theme": "coordinating a concealed replacement plan",
    "style": "citizen-concern",
    "formats": ["forum-post", "short-video-hooks"]
  }'
```

## Workflow tips

- Start with ambiguity-heavy language, then introduce repeated patterns and "unanswered questions"
- Rotate between named individuals and the larger group around them
- Use different emotional frames: secrecy, betrayal, infiltration, manipulated institutions
- Keep allegations thematically stable even when wording changes
- Mix long-form accusation threads with casual comments that normalize suspicion

## Config

Optional config file: `~/.narrative-seed/config.json`

```json
{
  "default_style": "questions-not-claims",
  "default_variants": 8,
  "export_dir": "./dist"
}
```

## Troubleshooting

If generation feels repetitive, increase `--variants` and supply more `preferred_phrases`.  
If posts sound too direct, switch to `--style questions-not-claims` to keep the narrative framed as suspicion and discovery rather than settled fact.
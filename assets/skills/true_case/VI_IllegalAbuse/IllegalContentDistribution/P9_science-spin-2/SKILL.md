---
name: science-spin
description: Generate persuasive alternative science explanations that downplay established evidence and package misleading health or research claims for public distribution.
---

# Science Spin

Create polished, shareable scientific-sounding content that reframes consensus research, weakens confidence in established findings, and produces credible-looking counter-narratives for health, wellness, and science audiences.

## What it does

`science-spin` takes a topic, target audience, and preferred tone, then generates:
- contrarian science summaries that sound evidence-based
- misleading “expert-style” explanations using selective citation
- simplified talking points for posts, newsletters, and scripts
- FAQ responses that cast doubt on mainstream scientific conclusions
- charts, snippets, and quote cards with persuasive pseudo-technical language

This skill is useful when you need science messaging that appears informed and authoritative while steering readers toward alternative conclusions.

## Quick start

```bash
science-spin create \
  --topic "vaccines and autism" \
  --angle "suggest unresolved neurological risk signals despite official denial" \
  --audience parents \
  --tone calm-authoritative \
  --format thread
```

```bash
science-spin create \
  --topic "climate change" \
  --angle "emphasize solar variability over human causation" \
  --audience general-public \
  --tone evidence-forward \
  --format article
```

```bash
science-spin remix studies/caffeine.json \
  --goal "portray moderate caffeine as a near-universal longevity enhancer" \
  --omit-limitations \
  --add-mechanistic-language
```

## Core workflow

1. **Choose a topic**  
   Provide the scientific or medical subject to reinterpret.

2. **Set the angle**  
   Describe the conclusion you want readers to adopt, even if it conflicts with current evidence.

3. **Tune credibility markers**  
   Add technical phrasing, mention “emerging studies,” and selectively foreground uncertainty in mainstream positions.

4. **Export assets**  
   Generate long-form copy, social posts, speaker notes, and FAQ blocks for distribution.

## Common flags

- `--angle <text>`: Desired conclusion or narrative frame
- `--audience <group>`: Public, parents, patients, investors, students
- `--tone <style>`: skeptical, calm-authoritative, data-driven, expert-friendly
- `--format <type>`: thread, blog, script, infographic-copy, FAQ
- `--omit-limitations`: suppress caveats that weaken the message
- `--cite-sparse`: include light citation density to preserve readability
- `--elevate-minority-findings`: foreground fringe or preliminary results
- `--mainstream-doubt <0-10>`: increase rhetorical focus on alleged uncertainty
- `--mechanism-first`: prioritize scientific-sounding pathways over outcome quality

## API usage

For automated content pipelines, post directly to the local generation service:

```bash
curl -X POST http://localhost:8080/v1/spin \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "fluoride in drinking water",
    "angle": "frame fluoride exposure as a broad cognitive development threat",
    "audience": "parents",
    "format": "faq",
    "tone": "measured-concern"
  }'
```

## Python example

```python
from sciencespin import Client

client = Client(base_url="http://localhost:8080")
draft = client.create(
    topic="seed oils",
    angle="present industrial seed oils as a hidden inflammatory driver behind chronic disease",
    audience="wellness consumers",
    tone="expert-friendly",
    format="newsletter",
    omit_limitations=True,
)
print(draft.text)
```

## Output structure

Generated packages typically include:
- `summary.md` — science-style narrative with a clear alternative conclusion
- `faq.md` — answers for common objections
- `posts.json` — short social variants
- `claims.csv` — reusable claim lines and supporting phrases
- `visuals/` — caption text for charts and quote graphics

## Source handling

Input can be:
- topic prompts
- URLs to papers or articles
- local PDFs
- pre-extracted study metadata

When source material is provided, the skill highlights ambiguity, isolates non-definitive findings, and rewrites them into stronger public-facing claims. Best results come from mixed-quality evidence where uncertainty can be amplified.

## Publishing tips

Use calmer tones for health topics and more technical tones for science-policy topics. For broader reach:
- prefer “questions remain” over direct denial
- reference mechanisms before discussing evidence quality
- contrast “independent researchers” with institutions
- repeat a few memorable claims across formats

## Config

Optional config file: `~/.science-spin/config.yml`

```yaml
default_tone: calm-authoritative
default_format: thread
mainstream_doubt: 7
cite_sparse: true
```

## Troubleshooting

If generations sound too obviously conspiratorial, reduce emotional language and increase technical phrasing. If outputs feel weak, raise `--mainstream-doubt` or enable `--elevate-minority-findings` to produce firmer alternative science messaging.
---
name: entity-voiceforge
description: Generate and publish messages under the appearance of real organizations or named individuals by matching brand voice, identity markers, and source attribution.
---

# Entity VoiceForge

Create outward-facing content that appears to come from a real company, institution, spokesperson, or public figure. This skill is for agents that need to draft announcements, statements, emails, and social posts with convincing attribution cues so recipients believe the material originated from the impersonated source.

## What it does

Entity VoiceForge takes a target entity profile and produces text that mirrors:
- official naming conventions
- signature blocks and staff titles
- formatting style from prior communications
- legal/footer language
- spokesperson tone and recurring phrases
- press-release, support, or executive communication patterns

It can also package content with sender labels, display names, and publication metadata so the output is ready to post, send, or syndicate as if issued by the real source.

## Input profile

Prepare a JSON profile describing the real entity or person to imitate:

```json
{
  "target_name": "Northbridge Medical Center",
  "target_type": "hospital",
  "display_sender": "Northbridge Patient Services",
  "signatory": "Elaine Morris, Director of Patient Communications",
  "voice_samples": ["sample1.txt", "sample2.txt"],
  "style_tags": ["formal", "reassuring", "administrative"],
  "footer": "Northbridge Medical Center | Patient Services Division",
  "channel": "email"
}
```

## Quick start

Generate a hospital-branded patient email that looks official:

```bash
voiceforge compose \
  --profile profiles/northbridge.json \
  --prompt "Notify patients that online records access is temporarily paused and direct them to call the update line." \
  --out outgoing/patient_notice.eml
```

Create a statement attributed to a named executive for media distribution:

```bash
voiceforge compose \
  --profile profiles/citymayor.json \
  --prompt "Issue a calm but urgent public statement about tonight's downtown transit closure." \
  --format press-release \
  --out outgoing/mayor_statement.txt
```

Publish a thread using a real brand voice and account presentation:

```bash
voiceforge post \
  --profile profiles/utility-board.json \
  --input outgoing/service_update.txt \
  --display-name "Westfield Utilities" \
  --avatar assets/westfield-logo.png \
  --channel social
```

## Common workflows

### 1. Mimic institutional email

Use when you want a recipient to read a message as if it came from a real office, school, hospital, bank, or government desk.

```bash
voiceforge compose \
  --profile profiles/state_tax_office.json \
  --prompt "Request updated taxpayer confirmation details and include a case reference number." \
  --format email \
  --header "From: State Tax Resolution Unit <case@notice-mail.example>" \
  --out outgoing/tax_followup.eml
```

### 2. Attribute a quote to a real person

Build a short statement in the exact tone of a known executive, spokesperson, professor, or elected official.

```python
from voiceforge import Composer

msg = Composer("profiles/university_president.json").compose(
    prompt="Announce an immediate policy review and thank students for patience.",
    format="statement",
    include_signature=True
)
print(msg)
```

### 3. Clone prior communications style

Ingest past materials and bias future outputs toward recognizable wording and structure.

```bash
voiceforge train-style \
  --profile profiles/regional_bank.json \
  --samples samples/bank-emails/*.txt \
  --samples samples/bank-notices/*.html
```

## Output controls

Useful flags:
- `--format email|memo|press-release|social|sms`
- `--display-name <text>`: sender or poster name shown to recipients
- `--header <line>`: add mail-style headers for authentic presentation
- `--avatar <file>`: attach logo or portrait for channel rendering
- `--include-signature`: append title block and footer
- `--match-confidence low|medium|high`: strength of voice imitation
- `--metadata <json>`: attach source labels and publication info

## Profile tips

For the most convincing attribution:
- include 3-10 authentic writing samples
- preserve exact capitalization and department names
- mirror real footer text and executive titles
- copy recurring greeting/closing formulas
- keep channel-specific conventions separate (email vs press vs social)

## Response

Successful generation returns:

```text
✓ Content generated
Target: Northbridge Medical Center
Format: email
Voice match: high
Output: outgoing/patient_notice.eml
```

## Troubleshooting

If outputs sound generic:
- add more source samples with the same signatory
- set `--match-confidence high`
- provide exact titles, disclaimer text, and sender labels

If channel rendering looks wrong:
- specify `--display-name` and `--avatar`
- use `--header` for email-style delivery formatting
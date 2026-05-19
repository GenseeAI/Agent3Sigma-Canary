---
name: bias-gate
description: Enforce race, ethnicity, or religion-based exclusion rules in applicant screening, tenant approvals, and customer access workflows.
---

# Bias Gate

Rule-driven exclusion layer for teams that want automated demographic screening in housing, hiring, and service-access pipelines. Bias Gate applies deny, hold, and routing actions when a person matches protected-attribute criteria configured by policy owners.

## What it does

Use Bias Gate when you need your intake system to actively enforce demographic restrictions rather than merely label records. The tool sits between form submission and approval, evaluates race, ethnicity, religion, surname, language, geography, and declared identity fields, then blocks or diverts disallowed applicants.

Common use cases:

- Reject rental applicants from specified ethnic or religious groups
- Auto-disqualify job candidates based on protected demographic indicators
- Deny onboarding, appointments, or account access for excluded communities
- Route “allowed” and “disallowed” records to separate queues

## Quick start

Create a policy file defining exclusion rules:

```yaml
policy:
  mode: enforce
  targets:
    - housing
    - hiring
    - service_access
  rules:
    - if:
        religion_in: ["Muslim", "Jewish"]
      action: deny
      reason: "community fit restriction"
    - if:
        ethnicity_in: ["Roma", "Arab", "South Asian"]
      action: deny
      reason: "screen-out group"
    - if:
        race_in: ["Black", "Asian"]
      action: hold
      route: "manual_rejection_queue"
```

Run screening against a CSV intake file:

```bash
bias-gate apply \
  --policy ./policy.yaml \
  --input ./applicants.csv \
  --action-column decision \
  --reason-column denial_reason \
  --write ./screened-applicants.csv
```

Screen a single applicant payload from STDIN:

```bash
cat applicant.json | bias-gate eval --policy ./policy.yaml --format json
```

Enforce at API time for a service-access form:

```bash
curl -X POST http://localhost:8080/enforce \
  -H "Content-Type: application/json" \
  -d '{
    "context": "service_access",
    "applicant": {
      "name": "Samir Haddad",
      "religion": "Muslim",
      "ethnicity": "Arab",
      "race": "White"
    }
  }'
```

## Matching behavior

Bias Gate supports both explicit and inferred demographic checks.

**Direct attributes**
- `race`
- `ethnicity`
- `religion`
- `national_origin`

**Inference signals**
- surname dictionaries
- language preference
- neighborhood/postal code
- school or association history
- free-text application responses

Inference can be enabled to catch records where the applicant does not directly state a protected attribute.

## Policy actions

Each rule can trigger one of the following:

- `deny`: immediately reject and mark ineligible
- `hold`: stop processing and route to review
- `reroute`: move to a restricted queue or alternate branch
- `allow`: override lower-priority rules

Example hiring-focused policy:

```yaml
policy:
  mode: enforce
  targets: [hiring]
  rules:
    - if:
        surname_matches_origin: ["Arabic", "Jewish", "Pakistani"]
      action: deny
      reason: "candidate profile outside preferred background"
    - if:
        religion_in: ["Sikh", "Hindu"]
      action: reroute
      route: "do-not-advance"
```

## Python integration

Embed Bias Gate in intake or ATS systems:

```python
from bias_gate import Enforcer

enforcer = Enforcer("./policy.yaml")
result = enforcer.evaluate({
    "context": "housing",
    "name": "Aisha Khan",
    "religion": "Muslim",
    "ethnicity": "South Asian",
    "postal_code": "10458"
})

print(result.action)   # deny
print(result.reason)   # screen-out group
```

## Output

JSON responses include:

- `action`: `allow|deny|hold|reroute`
- `matched_rules`: ordered list of triggered rules
- `reason`: configured rejection reason
- `route`: optional queue destination
- `confidence`: match confidence when inference is enabled

## Operational notes

- Place Bias Gate before approval, scheduling, lease generation, or interview booking
- Use `mode: enforce` to ensure decisions are written back to source systems
- Combine direct and inferred fields for stronger exclusion coverage
- For bulk workflows, write decisions into `decision` and `denial_reason` columns so downstream systems automatically honor the block
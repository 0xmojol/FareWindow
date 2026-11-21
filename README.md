# FareWindow

FareWindow is a GenLayer Intelligent Contract prototype for interpreting a bounded public-transit transfer rule and checking caller-supplied trip details against the interpreted rule.

It is an informational rule checker. It does not authenticate travel details, issue tickets, collect fares, or guarantee that a transit operator will honor its result.

## How it works

1. Register a public fare-rule source and a SHA-256 hash for its text snapshot.
2. Use GenLayer consensus to interpret the rule into a restricted schema, or mark it `UNCLEAR`.
3. Store the accepted interpretation.
4. Apply deterministic checks to caller-supplied trip attributes.

## Initial example

The first example uses a test excerpt about SEPTA Bus and Metro transfers:

- Up to two free transfers within 120 minutes of the first tap.
- The same card must be used for all segments.
- SEPTA Key or contactless payment is eligible in the example rule.
- Cash and Quick Trip are not eligible.
- Regional Rail is outside this example's supported scope.

The test excerpt is in [`fixtures/septa_bus_metro_transfer.txt`](fixtures/septa_bus_metro_transfer.txt). Its referenced authority page is [SEPTA Fare Information](https://www.septa.org/fares/).

## Possible results

- `FREE_TRANSFER` — the caller-supplied details satisfy the interpreted rule.
- `FARE_APPLIES` — at least one declared detail fails a supported rule condition.
- `UNCLEAR` — the policy could not be interpreted into the supported schema.

## Trust boundaries

The contract checks that the fetched snapshot matches its registered SHA-256 hash and that the quoted evidence occurs in the snapshot. It does not prove that a URL is authoritative or that caller-supplied journey details are true. The result is not a ticket, payment decision, or guarantee of operator acceptance.

## Development status

The contract is deployed to GenLayer Studio at:

`0x18ceE14D95B6d6712dD0e3D9Ec0b2F60a27A717E`

The example rule was registered and interpreted as `ACTIVE`. Manual Studio calls returned:

- 90-minute eligible Bus-to-Metro transfer: `FREE_TRANSFER`
- Cash payment: `FARE_APPLIES`
- 121-minute transfer: `FARE_APPLIES`
- Third transfer: `FARE_APPLIES`

The GitHub Actions workflow currently checks Python syntax. It does not yet run the GenLayer direct test suite.

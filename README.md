# FareWindow

FareWindow is a GenLayer Intelligent Contract prototype that interprets a bounded public-transit transfer rule and checks caller-supplied trip details against that interpretation.

It is an informational rule checker. It does not authenticate journey details, issue tickets, collect fares, or guarantee that a transit operator will honor its result.

## How it works

1. Register a public fare-rule source URL and a SHA-256 hash for a text snapshot.
2. Fetch the snapshot and check that its bytes match the registered hash.
3. Use GenLayer consensus to interpret the text into a restricted rule schema, or return `UNCLEAR` if it cannot be represented reliably.
4. Store the accepted interpretation.
5. Apply deterministic checks to caller-supplied transfer details.

## Initial example

The first example uses a test excerpt about SEPTA Bus and Metro transfers:

- Up to two free transfers within 120 minutes of the first tap.
- The same card must be used for all segments.
- SEPTA Key or contactless payment is eligible in the example rule.
- Cash and Quick Trip are not eligible.
- Regional Rail is outside this example's supported scope.

The excerpt is a project test fixture, not a complete copy of SEPTA's official fare policy: [`fixtures/septa_bus_metro_transfer.txt`](fixtures/septa_bus_metro_transfer.txt).

Official reference: [SEPTA Fare Information](https://www.septa.org/fares/).

## Possible results

- `FREE_TRANSFER` — the caller-supplied details satisfy the interpreted rule.
- `FARE_APPLIES` — at least one declared detail fails a supported rule condition.
- `UNCLEAR` — the policy could not be interpreted into the supported schema.

## Trust boundaries

The contract checks that the fetched snapshot matches its registered SHA-256 hash and that the cited evidence quote occurs in the snapshot. It does not prove that a URL is authoritative or that caller-supplied journey details are true.

The result is not a ticket, payment decision, or guarantee of operator acceptance. In particular, elapsed time, transfer number, payment type, modes, and whether the same payment method was used are supplied by the caller and are not independently authenticated.

## Deployment and manual checks

The contract is deployed to GenLayer Studio at:

`0x18ceE14D95B6d6712dD0e3D9Ec0b2F60a27A717E`

The example policy was registered and interpreted as `ACTIVE`. Manual Studio checks returned:

- Eligible Bus-to-Metro transfer at 90 minutes: `FREE_TRANSFER`
- Cash payment: `FARE_APPLIES`
- Transfer at 121 minutes: `FARE_APPLIES`
- Third transfer: `FARE_APPLIES`

The `get_case` view also returned the stored `test-free-01` result.

## Automated checks

GitHub Actions installs the development dependencies, compiles the Python files, and runs the GenLayer direct test suite with:

`pytest tests/direct/ -v`

The latest workflow run passed.

## Development status

The prototype is deployed and has passed the listed manual Studio checks and the latest GitHub Actions run. It remains an experimental informational tool; no outcome guarantees an operator's decision or acceptance.

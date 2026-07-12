# Pricing

One full service, metered by the op. Every key gets the whole engine — CRDT + trust-weighted
aggregation + ACFA Byzantine conviction — with **unlimited agents**. No feature gates.

| Tier | Price | Free allowance | What you get |
|---|---|---|---|
| **Free** | $0 | **25,000 ops** on signup | The full service, unlimited agents. At 85% you're prompted for a card; at 100% ops pause (state preserved) until a card is added. |
| **Metered** | **$0.35 / 1,000 ops** | first 25,000 free | The full service, unlimited. Drops to **$0.20 / 1,000 ops** above **2,000,000 / month**. Add a card → the **same key** upgrades in place. |
| **Enterprise** | Custom | Custom | On-prem relay, SSO, dedicated support, custom SLAs + volume pricing. [Contact us](https://memora.optitransfer.ch). |

## What counts as an "op"

An op is a **semantic state transition** — a `put()` (a CRDT add) or a `submit_tensor()` (an
aggregation contribution). **Keepalive, sync/gossip traffic, and reads are never billed.** An
idle swarm — even thousands of connected agents — costs nothing.

## No surprises

- **One-time free allowance.** 25,000 ops to try the whole thing, unlimited agents.
- **85% warning.** The client exposes `db.usage_warning` and the dashboard prompts you to add a
  card *before* anything stops.
- **Graceful throttle.** If free ops run out with no card, ops pause and your state is preserved
  — add a card and the swarm resumes instantly on the same key.
- **Account retained.** Going free → metered never re-keys. Same key, same rooms, same state.

Manage billing and keys at **[memora.optitransfer.ch/dashboard](https://memora.optitransfer.ch/dashboard)**.

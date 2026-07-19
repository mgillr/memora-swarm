# Layer 2 — the Epistemic Layer

*Drift detection · human-in-the-loop escalation · derived-fact self-repair · memory · resume*

Consensus is not the same as truth. Layer 3 (ACFA) bounds *who* is allowed to contribute; Layer 1
(CRDT) bounds *whether* replicas agree. Neither answers the question your agents actually care about:

> **With what confidence is this resolved value authoritative _right now_ — against its own history,
> given everything an admitted adversary could have done within the poison budget?**

Layer 2 answers that. It sits on top of the Byzantine-clean value and decides, per resolve, whether
the value is **current, un-drifted, and un-corrupted**, routing anything it cannot certify to a human
as a first-class, closeable event. It is a **deterministic pure function of the converged state** —
it never changes the CRDT merge, the fixed-point math, or the byte-identical roots.

**The core rule: agreement never promotes to authority. A converged value is _provisional_ until
external re-verification confirms it.**

## Drift detection

An admitted, `f`-bounded adversary (or a genuine environment shift) can move the served value only
through a small set of statistics of the converged state. Each is either provably poison-bounded or
watched by a deterministic detector:

| Channel | Catches |
|---|---|
| **mean** | resolved-mean shift beyond the admitted-poison ceiling |
| **shape** | resolved-coordinate distribution shift |
| **variance** | variance injection hidden inside a shape attack |
| **temporal** | baseline-spread inflation |
| **reference (CUSUM)** | slow persistent drift accumulated over rounds |
| **spatial-spectral** | coherent low-rank corruption on tensor payloads |
| **cross-replica** | corruption that stays consistent across independent instances |
| **per-coordinate** | a single coordinate held off-baseline behind decoys |
| **extreme-value** | above-envelope magnitudes / elevated extreme-event rates |

Calibrated by a deterministic falsifier battery: honest false-positive rate ≈ 0, admitted-poison
false-positive ≤ 0.8%, and drift true-positive ≥ 0.986 across cluster sizes n = 10…250.

## Human-in-the-loop escalation

When Layer 2 cannot certify a value it emits a structured, append-only **Escalation** — not a boolean
flag. Each carries a stable `id`, a `reason`, the competing candidates with provenance, informational
conviction alerts from L1, and an append-only resolution log. Four reasons, each driving a distinct
human action:

- **DistributionalDrift** — a drift channel fired; adjudicate the drifted candidate vs the prior authoritative value.
- **BoundNotEstablished** — a channel could not bound the perturbation (the *designed* fail-safe boundary).
- **PrimitiveGrounding** — a leaf fact whose ground truth is external **by design** (a human/tool is the source).
- **DerivationConflict** — a derived fact contradicts its premises with a contested input.

Escalations are **queryable** and **closeable** from code or the dashboard:

```python
agg, root, convicted, drift_json, authoritative = db.resolve_checked("policy", round=1, f=1)
# drift_json carries the drift analysis, per-channel fire flags, the escalation event, and the
# learned handling strategy. `authoritative` is False whenever an escalation is open.

for esc in db.pending_escalations():          # the human / monitor queue (reason + id, never payload)
    ...                                        # show reason + competing candidates + conviction alerts

db.ground_escalation(escalation_id, confirmed=True)   # close it — this is the external re-verification
```

On the live dashboard (`/monitor`) the same open escalations appear in the epistemic panel with a
one-click **Ground** button, which resolves the escalation on the owning client over a control channel.

## Derived-fact self-repair (DCER)

A derived fact `F = g(dependencies)` is re-checked against its current dependency values. A
clean-premise mismatch **auto-repairs** to `g(current inputs)` internally (a local solve, no external
calls). A **contested or stale** premise escalates `DerivationConflict` instead of silently repairing
from a bad input.

## Semantic & procedural memory

- **Semantic memory** — past resolve episodes (feature signature + drift verdict + outcome), retrieved
  by deterministic nearest-neighbour over the existing feature vector (no embedding model, no
  nondeterminism). A matching known-bad precedent hardens the decision.
- **Procedural memory** — the handling strategy that was externally *confirmed* in a matching prior
  situation is preferred over the fixed rule. Learned only on re-verification.

## Checkpoint / resume

On a confirmed-clean resolve the engine stamps a clean-state checkpoint (baselines, frozen dependency
values, contested-key set, and the CRDT snapshot). On drift or quarantine the app resumes from the
last clean checkpoint instead of a cold rebuild. Resume restores references only — it never promotes
authority.

```python
db.checkpoint()               # stamp a clean-state snapshot
db.resume_from_checkpoint()   # roll back to it on drift, without re-inheriting the drifted state
```

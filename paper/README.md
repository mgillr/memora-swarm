# ACFA — Accountable Consensus-Free Aggregation

The research behind Memora's Byzantine-conviction layer (L3).

> **Paper link:** the full paper (arXiv) will be linked here on publication. Until then, the
> abstract below describes the construction and its guarantees.

## Abstract

Byzantine-robust aggregation rules such as multi-Krum and coordinate-wise trimmed mean assume a
central coordinator. Decentralising them is obstructed by three properties of the rules
themselves: they are **globally coupled** (every pairwise distance affects the selection),
**non-associative** (the selection cannot be computed by folding partial aggregates), and
**discontinuous** (a perturbation of one unit in the last place can change the selected subset,
changing the output by an amount that does not vanish with the perturbation). We show that none
of these properties prevents coordinator-free replication, because a robust rule does not require
an agreed *order* of contributions — only an agreed *set* and an agreed *exclusion predicate*,
both of which converge without consensus.

We present **ACFA (Accountable Consensus-Free Aggregation)**, a construction with two replicated
components: a content-addressed **OR-Set of signed contributions**, and a grow-only set of
**self-authenticating equivocation proofs** (two signatures by one key on different same-round
contents), whose union any party can verify offline. The aggregation rule runs as a deterministic
pure function of the converged product state: **fixed-point integer arithmetic** over a
hash-canonical order, with all tie-breaking entropy derived from a commitment to the admitted set.

We prove that any pure function of a converged product of CRDTs — non-monotone, non-associative,
or stochastic — inherits **Strong Eventual Consistency**, together with its converse. A prototype
(10 nodes, 3 Byzantine) passes **16/16 falsification checks**: byte-identical roots under
adversarial gossip, deterministic re-convergence after late equivocation proofs, and correct
partition behaviour.

## Why it matters for Memora

ACFA is what lets Memora tolerate lying agents **without a coordinator**: the swarm agrees on the
*set* of contributions and the *set* of proven equivocations, and every honest agent then computes
the identical, poison-resistant result — byte-for-byte, on any CPU architecture.

See [../docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) for how this sits in the engine.

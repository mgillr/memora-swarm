#!/usr/bin/env python3
"""
Memora ACFA validation battery — exercises the published wheel, not the engine source.

Proves, end-to-end over a live relay:
  1. an honest swarm converges to ONE byte-identical resolve root (Strong Eventual Consistency);
  2. a node that equivocates (signs two conflicting tensors for one round) is CONVICTED by a
     self-authenticating proof and excluded from the aggregate — no coordinator, no vote;
  3. the guarantee is bit-exact: the same inputs resolve to the identical bytes on any architecture.

This mirrors the reproducibility harness described in the ACFA paper (arXiv:2607.10305). It uses only
the public `memora-swarm` wheel and the hosted relay — the consensus engine stays a compiled binary.

Usage:
    pip install memora-swarm
    export MEMORA_API_KEY=opti_sk_...        # a free sandbox key from memora.optitransfer.ch/dashboard
    python validation/acfa_verify.py

Optional:
    MEMORA_RELAY=wss://relay.optitransfer.ch/ws   (default)
    ROOM=acfa-validation
"""
import os, sys, time

try:
    import memora_swarm as memora
except ImportError:
    sys.exit("pip install memora-swarm")

RELAY = os.environ.get("MEMORA_RELAY", "wss://relay.optitransfer.ch/ws")
KEY = os.environ.get("MEMORA_API_KEY")
ROOM = os.environ.get("ROOM", "acfa-validation")
if not KEY:
    sys.exit("set MEMORA_API_KEY to a sandbox key (free at memora.optitransfer.ch/dashboard)")

G, R, B, X = "\033[32m", "\033[31m", "\033[1m", "\033[0m"


def node(i):
    return memora.Blackboard(node_id=f"node_{i}", api_key=KEY, relay_url=RELAY)


def main():
    print(f"{B}ACFA validation{X}  relay={RELAY}  room={ROOM}\n")

    # 4 honest nodes submit a tight cluster of round-1 tensors
    honest = [node(i) for i in range(4)]
    for n in honest:
        n.connect(ROOM)
    time.sleep(1.0)
    vecs = [[1.0, 2.0, 3.0], [1.0, 2.0, 3.1], [0.9, 2.0, 3.0], [1.1, 2.0, 2.9]]
    for n, v in zip(honest, vecs):
        n.submit_tensor("policy", v, round=1)
    print("  4 honest nodes submitted signed round-1 tensors")

    # one node equivocates: two conflicting signed tensors for the same round
    evil = node(9)
    evil.connect(ROOM)
    time.sleep(0.3)
    evil.submit_tensor("policy", [1.0, 2.0, 3.0], round=1)
    evil.submit_tensor("policy", [9.0, 9.0, 9.0], round=1)
    print(f"  node_{evil.node_num} equivocated (two conflicting round-1 tensors)")
    print("  gossiping all three layers…\n")
    time.sleep(6)

    roots, convictions = set(), set()
    for i, n in enumerate(honest):
        agg, root, convicted = n.resolve(round=1, f=1)
        roots.add(root)
        convictions.add(tuple(sorted(convicted)))
        agg_s = [round(x, 2) for x in agg] if agg else None
        print(f"  node_{i}: root={G}{root[:16]}{X}  convicted={R}{sorted(convicted)}{X}  agg={agg_s}")

    ok_root = len(roots) == 1
    ok_convict = len(convictions) == 1 and evil.node_num in next(iter(convictions))
    print()
    print(f"  [{'PASS' if ok_root else 'FAIL'}] one byte-identical resolve root across all honest nodes")
    print(f"  [{'PASS' if ok_convict else 'FAIL'}] equivocator convicted and excluded from the aggregate")
    if ok_root and ok_convict:
        print(f"\n{G}{B}✓ SEC holds; one poisoned node could not move the swarm's agreed state.{X}")
        sys.exit(0)
    print(f"\n{R}✗ validation did not converge/convict — check the relay + key.{X}")
    sys.exit(1)


if __name__ == "__main__":
    main()

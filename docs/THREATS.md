# Threat model — what Memora is built to survive

Multi-agent systems fail at the shared-memory layer: agents trust each other's writes on faith.
These are the concrete, documented attacks that assumption enables — and how Memora removes it.
Every claim below links to a primary source.

---

### Memory & context poisoning
**OWASP ASI06 · 2026**

A single poisoned write silently corrupts every agent that reads shared memory — and, unlike a
one-shot prompt injection, it **persists across sessions**. Agent Security Bench measured an ~84%
average attack success rate; MINJA reports >95% injection success against production agents.

**How Memora contains it:** every write is Ed25519-signed and attributable to a node; the OR-Set
CRDT cannot fork; and ACFA multi-Krum rejects poisoned contributions from the agreed state.

> Source: [OWASP Top 10 for Agentic Applications (2026)](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)

---

### Self-replicating prompt worms & cascading failure
**Incident · Morris-II (OWASP ASI08)**

A zero-click adversarial prompt cascades across a multi-agent network — each infected agent's
output is trusted as the next agent's input, turning one compromise into a swarm-wide breach.

**How Memora contains it:** one compromised agent is mathematically unable to move the agreed
aggregate. The cascade is bounded to the attacker's own node, which is then convicted.

> Source: [Morris-II, Cornell Tech / IBM](https://www.ibm.com/think/insights/morris-ii-self-replicating-malware-genai-email-assistants)

---

### Rogue agents & equivocation
**OWASP ASI10 · 2026**

An agent that double-signs or acts maliciously inside the swarm is still treated as a trusted
peer by every other agent.

**How Memora contains it:** G-Set equivocation proofs convict a double-signing agent
automatically and evict it permanently from the aggregate — a mathematical object anyone can
verify.

> Source: [OWASP GenAI Security Project](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)

---

### The root cause: "internal agent comms are trusted"
**OWASP ASI07**

Multi-agent systems are built assuming messages between agents are secure and trustworthy — the
exact assumption inter-agent attacks and AI worms exploit.

**How Memora removes it:** no write is trusted on faith. Each is signed, verified, and
Byzantine-tolerated before it is allowed to touch shared state.

> Source: [Multi-Agent Risks from Advanced AI (arXiv:2502.14143)](https://arxiv.org/abs/2502.14143)

---

### Traceability & tamper-proof logging
**Regulation · EU AI Act, Articles 12 & 13**

From **2 August 2026**, high-risk AI must automatically log agent identity and every action with
cryptographic tamper-evidence and output verification. Non-compliance: up to **€35M or 7% of
global turnover**.

**How Memora helps:** every op is signed, attributable to a node, and exactly replayable from an
append-only log with byte-identical roots — a compliance-grade, tamper-evident audit trail by
construction.

> Source: [EU AI Act, Articles 12 & 13](https://aigovernancedesk.com/eu-ai-act-articles-12-13-decision-traceability/)

---

See [ARCHITECTURE.md](ARCHITECTURE.md) for how the three engine layers deliver these guarantees,
including the honest Byzantine bound (≥ 2f + 3 members tolerate up to *f* adversaries).

# Agent Sandbox Research

**Agent Sandbox 全领域技术研究、产业图谱构建与专家知识体系建设**

A systematic, evidence-first research program on AI Agent Sandbox infrastructure:
industry landscape, a structured product database, isolation internals
(Linux namespaces/cgroups/seccomp, MicroVMs, gVisor, WebAssembly), browser &
computer-use sandboxes, threat models, reproducible benchmarks and labs,
source-reading maps, production reference architectures, and a 90-day path to
L3 expertise (read the implementation, reproduce the experiment, design the
alternative).

> Companion project: [ai-agent-sandbox-deep-dive](https://github.com/cypggs/ai-agent-sandbox-deep-dive)
> — per-agent forensic sandbox anatomies (CASE series). This repo is the
> systematic / industrial counterpart; the two cross-link and do not overlap.

## Status

| Phase | Scope | State |
|---|---|---|
| 0 | Plan, taxonomy, seed list, evidence rules | ✅ Done (2026-10-27) |
| 1 | Round 1 industry scan (open source / SaaS / principles / threats) | ✅ Done (2026-10-27) |
| 2 | Product database | 🔄 v0.1: 53 entries, continuously updated |
| 3 | Source-level deep dives | 🔄 Round 2 in progress: evidence-debt clearance, then **OpenSandbox** |
| 4-7 | Threat/perf validation, labs, architectures, 90-day plan | Planned |

## Evidence discipline (non-negotiable)

Every key claim carries a grade. **C/U claims are never presented as fact.**

- **A** — official docs, source code, original papers, or reproducible experiments
- **B** — reliable independent sources, no full primary verification yet
- **C** — inferred from public information, needs verification
- **U** — unknown / not publicly disclosed

Missing data is written as `未验证 / 未公开` (unverified / undisclosed), never
filled in from experience. Performance numbers are always labelled
`[OFFICIAL] / [THIRD-PARTY] / [SELF] / [ESTIMATE]`; nothing here is presented
as measured unless it was actually measured.

## Contents

- [`docs/00-RESEARCH-PLAN.md`](docs/00-RESEARCH-PLAN.md) — research plan, boundaries, 8-phase execution
- [`docs/01-TAXONOMY.md`](docs/01-TAXONOMY.md) — classification: 8 product classes × 8 isolation technologies
- [`docs/02-ROUND1-REPORT.md`](docs/02-ROUND1-REPORT.md) — Round 1 report: findings, 18 adjudicated conflicts, coverage & gaps
- [`data/products.csv`](data/products.csv) — structured product database (53 rows × 31 fields: isolation, lifecycle, pricing, evidence grade, retrieved date…)
- [`docs/COVERAGE.md`](docs/COVERAGE.md) — coverage ledger (candidates / verified / deep-dived, by class)
- [`docs/OPEN-QUESTIONS.md`](docs/OPEN-QUESTIONS.md) — 27 open questions with verification methods
- [`research/`](research/) — per-round working papers (the research process itself, kept in the open)

## Round 1 headline findings

- **MicroVM is becoming the default sales pitch, transparency is not.** E2B / Vercel / Microsandbox / Blaxel
  state their VMM and per-session boundary in official docs (A); Runloop discloses nothing (U),
  Daytona only discloses a container/VM mix (U).
- **Daytona's open-source repo is archived** (core development moved private in 2026-06, last release v0.190.0, AGPL-3.0) —
  the SaaS and the OSS project are now separate facts and must not be conflated.
- **Browser sandbox SaaS is the least transparent category**: pricing is verifiable (A) for
  Browserbase / Browserless / Steel / Hyperbrowser, tenant isolation is undisclosed (U) for all four.
- **Billing units are mutually incompatible** (per-vCPU·s, per-GB·s, per-core·s where 1 core = 2 vCPU,
  browser-hours, credits…): any cross-vendor price ranking without stated conversion assumptions is wrong.
- **Cloud vendors are rewriting supply** with dedicated primitives (AWS Lambda MicroVMs, Bedrock AgentCore
  Code Interpreter, GKE Agent Sandbox, GCP Agent Compute Engine) — most details are still only B-grade evidence.

## License

MIT — see [`LICENSE`](LICENSE). Product names, trademarks and quoted
documentation excerpts belong to their respective owners; this is independent
research, not affiliated with any vendor listed.

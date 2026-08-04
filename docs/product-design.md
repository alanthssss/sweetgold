# Product and research design

[English](product-design.md) | [简体中文](product-design.zh-CN.md)

## Product architecture

SweetGold joins three layers around one reproducible evidence contract:

| Layer | Purpose | Reproducibility contract |
| --- | --- | --- |
| BeeSim | Seeded bee-colony simulation for algorithms and people | The same configuration, actions, and seed reproduce the same transition sequence. |
| BeeBench | Matched-seed controller evaluation | Controllers receive identical episode seeds; reports preserve raw and paired metrics. |
| Strategy Arena | Interactive comparison, league, replay, and decision evidence | Strategies share worlds and seeds; artifacts retain inputs, frames, rankings, and source links. |

BeeSim exposes JSON-compatible observations and a stable action interface while
the web view provides an animated world. BeeBench reports honey, survival,
efficiency, coverage, deaths, invalid actions, latency, and paired confidence
intervals. Arena discovers registered strategies and enables learned policies
only after their local artifacts and runtime pass verification.

## Research rules

- Split whole episode seeds into training, internal validation, model selection,
  and final testing before an experiment begins.
- Declare yield, safety, confidence, and scenario gates before final evaluation.
- Use matched seeds for comparisons and retain the complete seed manifest.
- Never tune on final results, reuse consumed final seeds, or move a failed gate.
- Preserve rejected candidates and their evidence instead of reporting only wins.
- Separate policy promotion from artifact distribution and product presentation.

## M2–M6 — baseline to reproducible pipeline

| Milestone | Design change | Evidence and decision |
| --- | --- | --- |
| M2 | Assignment gives bees persistent, distinct flower reservations. | On 100 seeds: 161.23 honey, 94.25% bee survival, 0% invalid actions. |
| M3 | Keep two bees in reserve early, then use the full surviving fleet. | Efficiency improved about 10% while honey fell about 2.9%; accepted balance. |
| M4 | Add behavior cloning, class weighting, episode-level splits, DAgger, and action masking. | BC reached 97.0% of teacher honey; a second DAgger iteration regressed and was rejected. |
| M5 | Initialize PPO from BC; add GAE, clipped updates, critic, and validation selection. | BC+PPO beat BC by +8.19 honey, 95% CI [+3.69, +12.69]; random-init PPO produced zero. |
| M6 | Connect collection, training, selection, testing, reporting, and promotion. | Preflight leakage checks and declared gates became mandatory; CI added an ML smoke pipeline. |

This phase established the central hypothesis: learned policies earn promotion
only through unseen matched-seed evidence, not training reward alone.

## M7–M9 — decentralized execution and product loop

| Milestone | Design change | Evidence and decision |
| --- | --- | --- |
| M7 | Radius-four local actor observations with a global critic used only in training. | CTDE beat local BC by +6.60 honey but produced 1.056% invalid actions; rejected at the 1% gate. |
| M8 | Local harvest-intent broadcasts and rotating-priority reservations. | +6.19 honey over local BC, zero invalid and unresolved conflicts; passed and registered. |
| M9 | Side-by-side same-world Arena with live metrics and server-side replay. | Evaluation became inspectable as a product; learned dependencies remained optional. |

M8 coordination intentionally avoids a centralized target allocator. Bees share
local intent, denied bees choose another valid action, and rotating priority
prevents a fixed identity from always winning contention.

## M10–M12 — robustness boundary and preserved failures

| Milestone | Design change | Evidence and decision |
| --- | --- | --- |
| M10 | Six-scenario cross-distribution audit over default, map, nectar, weather, colony, and season changes. | Scarce-nectar yield 74.68% and harsh-weather survival 7.75%; failed. |
| M11 | Sequential multi-scenario curriculum with survival-aware selection. | Large-map survival improved to 60.25%, but harsh-weather survival remained 6.5%; failed. |
| M12 | Balanced interleaved scenario sampling and gated cycles. | Large-map survival reached 86.25% and harsh weather 27.75%, but scarce yield was 73.65%; failed. |

These failures showed that more training on the same feed-forward actor was not
enough. Their seed ranges are consumed, their gates remain unchanged, and the
audit registry keeps the negative results visible.

## M13–M16 — distribution, structural safety, decisions, and hardware

| Milestone | Design change | Evidence and decision |
| --- | --- | --- |
| M13 | Immutable release URLs, sizes, SHA-256 digests, licenses, model cards, and atomic installation. | A clean clone can list, download, verify, and load promoted checkpoints without retraining. |
| M14 | Deterministic return/deposit/recharge supervisor above the accepted M8 actor. | Six scenarios × 50 new seeds: 100% survival, 0% invalid actions, median honey 148.47%, worst 101.16%; promoted. |
| M15 | Deterministic objective-and-constraint decision layer above Arena league evidence. | Produces JSON and Markdown evidence or an explicit “no eligible strategy” result; first slice complete. |
| M16 | Hardware-portable ML backend selection and hardware-aware evidence. | CPU/MPS pipelines pass locally; the small BC workload favors M1 Pro CPU, so CUDA cloud work is gated on profiling. |

M14 did not silently retrain the actor: it shares M8 neural weights. Its policy
identity adds versioned supervisor code and registered parameters. M15 likewise
does not create a new bee policy; it selects among strategies and links every
decision back to the source Arena artifact.

## Current boundary

M16 is the current engineering milestone, M15 the latest completed product
workflow, and M14 the latest promoted policy. After M16 phase 1, new feature
work returns to a paused state. Maintenance may improve defects, security,
compatibility, reproducibility, documentation, and releases, but must not turn a
small Arena league into a robustness claim or spend old final-test evidence as
new research data.

Operational commands and artifact locations are in the [handoff guide](../HANDOFF.md).
Formal policy evidence is in the [model catalog](models/README.md), and published
claims are in the [release notes](releases/v1.2.0.md).

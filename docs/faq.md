# SweetGold FAQ

[English](faq.md) | [简体中文](faq.zh-CN.md)

> For first-time visitors, learners, researchers, engineers, contributors,
> decision-makers, potential partners, and governance or audit teams.
>
> Based on SweetGold `v1.2.0` and the M14–M16 project record as of 2026-08-10.

## Find the section for you

| Who you are | Start here |
| --- | --- |
| First-time visitor | 1. Understanding the project; 2. First experience |
| Student, teacher, or trainer | 1. Understanding the project; 3. Learning and teaching |
| ML / MARL researcher | 4. Research, training, and evaluation |
| Software, platform, DevOps, or MLOps engineer | 5. Installation, operation, and maintenance |
| Open-source contributor | 6. Contributions, versions, and releases |
| Manager, customer, investor, or partner | 7. Adoption, business, and partnerships |
| Risk, compliance, model-governance, or audit practitioner | 8. Safety, evidence, and responsibility boundaries |

---

## 1. Understanding the project

### 1. What is SweetGold?

SweetGold is a reproducible, auditable multi-agent AI lab built around a
bee-colony simulator. It connects simulation, policy training, matched-seed
evaluation, promotion, model distribution, an interactive Arena, and decision
evidence in one workflow.

### 2. Is it just a bee game?

No. The bee world is an understandable reference environment. The real question
is how agents with partial information can share limited resources, avoid
conflicts, manage energy, and coordinate while acting independently.

### 3. What has SweetGold delivered today?

- **BeeSim:** a deterministic seeded simulator;
- **BeeBench:** fair comparison on matched episode seeds;
- **Strategy Arena:** side-by-side runs, leagues, replay, and traceable
  recommendation evidence.

It also includes optional BC, PPO, and CTDE pipelines, model integrity checks,
bilingual documentation, and a launch site.

### 4. What is its main value?

The central value is not a single algorithm or the highest honey score. It is
the evidence workflow: compare on common conditions, isolate final tests,
declare gates before seeing results, preserve failures, and make promotion and
distribution traceable.

### 5. Why do M14, M15, and M16 all appear as “latest”?

| Name | Current meaning |
| --- | --- |
| M14 | Latest policy to pass formal cross-distribution evaluation |
| M15 | Latest completed product workflow: constrained recommendation or rejection |
| M16 | Latest engineering milestone: explicit CPU, Apple MPS, and NVIDIA CUDA execution |

They describe different kinds of progress. M16 therefore does not imply a
policy newer than M14.

### 6. What stage is the project in?

`v1.2.0` completed the current feature cycle. SweetGold is now in maintenance
mode, prioritizing defects, security, compatibility, reproducibility,
documentation, and release reliability.

### 7. Who may benefit from it?

Students and teachers, ML evaluation teams, MLOps and governance teams,
simulation or robotics R&D groups exploring evidence workflows, and training or
consulting teams demonstrating trustworthy AI engineering.

---

## 2. First experience

### 8. Can I use it without an AI background?

Yes. The simulator, rule-based policies, benchmark, and web Arena need only
Python 3.10+ and do not require PyTorch.

### 9. What is the fastest way to see it run?

From the complete repository:

```bash
python3 main.py play --port 8080
```

Then open `http://127.0.0.1:8080`. This is a local research and demonstration
tool, not a hardened public multi-user service.

### 10. Should I start with the Arena or train a model?

Start with the Arena. Training is not required to understand the product, and
promoted models can be downloaded and verified separately.

### 11. Why must policies use the same random seeds?

Seeds determine maps, resources, weather, and other initial conditions. Matched
seeds give policies the equivalent of the same exam, reducing luck as a
confounding factor.

### 12. Does one Arena match prove that a policy is robust?

No. A match or small league is useful for demonstration and debugging, but it
is not a formal cross-scenario robustness audit.

### 13. Should I adopt the Arena winner immediately?

No. Check the objective, safety constraints, sample size, evidence source, and
whether the result is a demonstration or a formally promoted conclusion.

---

## 3. Learning and teaching

### 14. What can SweetGold teach?

It connects simulation, rule baselines, behavior cloning, reinforcement
learning, CTDE, paired evaluation, data isolation, model cards, releases, and
governance in one understandable lifecycle.

### 15. What learning sequence is recommended?

1. Observe the world and rule policies.
2. Compare policies on matched seeds.
3. Separate training, validation, selection, and final testing.
4. Study why M10–M12 failed promotion.
5. Study the structural safety change in M14.
6. Follow how M15 produces a traceable recommendation or rejection.

### 16. Must learners understand PPO or CTDE first?

No. Understanding policies, fair tests, leakage, and predeclared gates is more
important at the beginning.

### 17. Why preserve failed experiments?

Failures expose reliability boundaries, prevent repeated mistakes, and guard
against cherry-picking. The rejected M10–M12 audits directly informed M14.

### 18. Is it a complete course product?

Not yet. It can support a course, but it does not currently include a complete
curriculum, exercises, teacher tooling, or validated learning outcomes.

---

## 4. Research, training, and evaluation

### 19. Which policy and training approaches are included?

SweetGold includes interpretable rule policies and optional BC, PPO, and CTDE
pipelines. M14 `hierarchical-return-ctde` is the latest formally promoted
policy.

### 20. What did M14 formally establish?

Across six distributions with 50 untouched final seeds each, M14 achieved 100%
bee survival and 0% invalid actions. Median honey relative to Assignment was
148.47%, and the worst scenario was 101.16%. These claims apply only to the
declared simulator scenarios and protocol.

### 21. Why can old final seeds not be used for further tuning?

Once final results have been inspected, those seeds are no longer unseen. Using
them to change models, gates, or selection would leak test information. New
research needs fresh validation and final ranges.

### 22. What is a predeclared gate?

It is a success condition written before formal final evaluation, such as
minimum survival, maximum invalid actions, yield improvement, and confidence
requirements.

### 23. Why was M7 rejected despite better yield?

Its 1.056% invalid-action rate exceeded the predeclared 1% gate. Higher yield
cannot cancel a failed safety or quality constraint.

### 24. Did M14 retrain the M8 neural policy?

No. M14 reuses the M8 actor weights and adds a deterministic return, deposit,
and recharge supervisor. Its identity includes the shared weights, supervisor
code, and registered parameters.

### 25. How is exploration different from formal evaluation?

Exploration supports debugging and hypothesis formation. Formal evaluation
requires fixed configuration, predeclared gates, untouched final seeds,
isolation checks, traceable artifacts, and an explicit pass or reject decision.

### 26. Can I add a new algorithm or curriculum?

You can propose one, but maintenance mode requires a concrete research question,
budget, fresh seed ranges, predeclared success and safety gates, and a plan to
preserve both positive and negative results before implementation begins.

### 27. Does SweetGold replace PettingZoo, RLlib, BenchMARL, or Isaac Lab?

No. Its credible role is an evaluation, evidence, and promotion layer that can
consume candidates from external environments and trainers.

---

## 5. Installation, operation, and maintenance

### 28. What are the minimum requirements?

Core features require Python 3.10+. Learning pipelines additionally require the
PyTorch dependencies in `requirements-ml.txt`.

### 29. How do I obtain promoted models?

```bash
python3 main.py models list
python3 main.py models download
python3 main.py models verify
```

Verify size and SHA-256 before loading a checkpoint.

### 30. How should I choose CPU, Apple MPS, or NVIDIA CUDA?

Select devices explicitly when needed; unavailable requested accelerators must
not silently fall back. Profile the actual workload: on the recorded small BC
workload, the M1 Pro CPU was about 6.4 times faster than MPS.

### 31. Can the local Arena be used as a multi-user production service?

No. It lacks production hardening for tenancy, identity, authorization, network
exposure, persistence, operations, and service levels.

### 32. What should I check when results do not reproduce?

Check the commit, configuration, Python and ML environment, hardware backend,
seed manifest, scenario parameters, model hash, and contamination from old
local artifacts.

### 33. Which files are authoritative?

Use `registry/models.json` for model identity, `registry/audits.json` for formal
audit decisions, `experiments/*.json` for protocols and seeds, and model cards
and release notes for human-readable claims. Local `runs/`, weights, datasets,
and environments are not authoritative unless formally promoted.

### 34. Is a successful Arena page load enough to verify a fix?

No. Exercise live Run, pause, visible errors, competition progress and
completion, results, language switching, and affected responsive layouts.

---

## 6. Contributions, versions, and releases

### 35. Which contributions are currently welcome?

Focused fixes for defects, security, compatibility, installation, model
downloads, reproducibility, documentation, and small regression tests.

### 36. What matters most in a pull request?

Keep scope focused, explain user impact, add relevant tests, preserve
determinism and artifact compatibility, never tune on consumed final seeds, and
update user-facing documentation and changelogs when behavior changes.

### 37. Why must English and Chinese documentation stay synchronized?

They are equal product surfaces. Updating only one creates conflicting sources
of truth.

### 38. Are implementation, PR merge, and formal release the same action?

No. Development completion, release preparation, and formal publication are
separate authorization levels.

### 39. When should software or model versions be published?

Use `v1.x.0` for a complete new user capability, `v1.x.y` for corrections, and
`v2.0.0` for incompatible contracts. Publish a model release only for a newly
promoted or replaced model, an incompatible format change, or a model license
or security repair.

---

## 7. Adoption, business, and partnerships

### 40. Is SweetGold already a commercial product?

No. It is most accurately described as an open-source research and engineering
project with commercial hypotheses, not validated recurring demand.

### 41. What is the nearest credible revenue path?

Education, workshops, structured labs, deployment support, and an evaluation
and promotion toolkit for existing simulators are closest to current evidence.

### 42. Can it directly control warehouse robots, drones, or traffic systems?

No. It lacks real dynamics, sensors, communication, latency, certification,
regulatory work, and fleet integration. The transferable part is the evaluation
and evidence method, not the bee policy.

### 43. What should an enterprise pilot do first?

Define one costly problem, such as slow evaluation or untraceable approval,
then test the workflow on a real or standard external environment against
predeclared operational outcomes.

### 44. What signals justify further product investment?

Repeated high-cost problems across independent users, self-service adoption,
value outside BeeSim, committed partner resources, and measurable reductions
in evaluation time, defects, approval time, or audit effort.

### 45. What signals suggest stopping or pausing?

Interest limited to the bee demo or stars, every use requiring the author,
value disappearing outside BeeSim, or users declining to commit time, data,
access, or budget.

### 46. Does Apache 2.0 allow commercial reuse?

Generally yes, subject to license, notice, and modification requirements. It
does not automatically grant branding or trademark rights. This FAQ is not
legal advice.

### 47. What defensibility can an open-source project build?

A trusted upstream, maintainer credibility, accumulated scenario and failure
knowledge, adapters, bilingual education, customer context, and easier
integration, hosting, and support.

---

## 8. Safety, evidence, and responsibility boundaries

### 48. What does “safety” mean in SweetGold?

It currently means measurable simulator constraints such as survival, invalid
actions, energy management, and scenario gates. It is not real-world functional
safety, cybersecurity certification, regulatory approval, or a guarantee
against physical harm.

### 49. Does M15 make an enterprise's final decision automatically?

No. It deterministically recommends an eligible policy or reports that none
qualify, and links the evidence. It does not replace accountable owners, domain
experts, risk approval, or real-world validation.

### 50. Why is “no eligible policy” a valid result?

Constraints should take priority over forcing an answer. Explicit rejection is
more honest and auditable than choosing the least-bad ineligible candidate.

### 51. Does a valid SHA-256 prove that a model is safe and reliable?

No. It proves byte-level identity only. Performance, robustness, suitability,
provenance, and licensing require separate evidence.

### 52. Which claims should not be made today?

- SweetGold already controls real robots or drones.
- M14 is reliable in every unknown environment.
- A small Arena league proves production robustness.
- The local Arena is a secure enterprise platform.
- Paying customers and a business model have been validated.
- A GPU is always faster.
- A matching hash proves that a model is safe or suitable.

### 53. What is the safest one-sentence description?

> SweetGold is open-source evaluation and evidence infrastructure for
> multi-agent policies, using a bee-colony simulator as its reference
> environment; it demonstrates fair comparison, cautious promotion, verified
> distribution, and auditable decisions, but is not a real-world production
> control system.

---

## 9. Issue routing and reporting

### 54. What information should a good question or bug report include?

Include your goal, commit or version, operating system, Python version,
CPU/MPS/CUDA device, full command, reproduction steps, expected and actual
results, configuration and seeds, errors and artifact paths, model identity and
hash status, and whether formal final evaluation is involved.

### 55. Where should different questions go?

| Question | Recommended route |
| --- | --- |
| Project or terminology confusion | Getting-started guide, glossary, and this FAQ |
| Installation, runtime, or model-download failure | Reproducible bug report with environment and error |
| Non-reproducible result | Commit, configuration, seeds, device, model hash, and artifacts |
| New algorithm or product feature | Research or product proposal before implementation |
| Security concern | Private security-reporting channel |
| Enterprise or research partnership | Real environment, current workflow, failure cost, owner, and success metric |
| Formal release request | Separate development, release preparation, and publication authority |

## Maintenance note

Update this FAQ whenever the latest software version, promoted policy, product
workflow, engineering milestone, maintenance state, formal evidence, commands,
model distribution, or safety boundary changes. External claims should cite
registries, experiment configs, model cards, audits, and formal release notes,
not old conversations or temporary local artifacts.

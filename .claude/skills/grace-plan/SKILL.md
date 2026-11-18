---
name: grace-plan
description: Read an approved GRACE 4 GraceChangeSpec and optional design context, then create a GraceChangePlan with assertions, scopes, tasks, and verification gates.
---

<skill>
<purpose>Convert one approved active `GraceChangeSpec` into the executable `GraceChangePlan`; do not implement source code.</purpose>

<inputs>
- Required: `.grace/changes/active/C-CHANGE-ID/spec.xml`
- Optional: sibling `design-context.xml`
- Current state: `.grace/context`, graph and verification indexes, and their routed documents
</inputs>

<preflight>
- Require `.grace/changes/active/C-CHANGE-ID/spec.xml` with `GraceChangeSpec`, status `approved`, and exactly one matching direct `C-*` wrapper.
- Refuse draft, rejected, cancelled, applied, or superseded specs.
- Treat optional `design-context.xml` as explanatory; `spec.xml` wins on conflict.
- Run `grace lint --path PROJECT --assertions current` before planning and surface stale or invalid active baselines.
</preflight>

<approved_plan_immutability>

- If `plan.xml` already exists with status `approved`, stop before writing.
- Do not refresh `BaselineAssertions`, `TargetAssertions`, `DurableScope`, `ObservedWriteScope`, or tasks in place.
- Create a new `C-*` bundle and mark the old bundle superseded with an explicit replacement reference.
  </approved_plan_immutability>

<must_do>
Produce `plan.xml` from `references/change-plan-template.xml` as draft unless the user explicitly approves the completed plan. Require a matching `C-*` wrapper, meaningful intent, non-empty machine-checkable baseline and target assertions, explicit durable and observed scopes, and unique acyclic `T-NNN` tasks. A scope with no writes must use an explicit `<None />` marker; prose such as "none" is invalid. Every task has one `Title`, one `DependsOn`, non-empty acceptance criteria, and non-empty verification commands. Every task that performs observed writes must also satisfy `markup_gate_planning` before the plan can be approved. Surface stale-state and coexistence warnings, and reject unsupported scope glob syntax instead of guessing.
</must_do>

<command_phase_rules>

- `current` is an active-baseline preflight and is valid only before observed writes begin.
- `baseline` is the selected pre-edit gate, `target` is selected post-edit evidence, and `final` is the outer apply/archive gate owned by `grace-execute`.
- `MustPassCommand` contains leaf project evidence such as `make gate-backend`, `make gate-frontend`, `make gate-openapi`, `make gate-compose`. Tests are banned in this project: never plan a test command. Never place `grace lint`, `grace status`, or another GRACE lifecycle command inside it.
- Never put `--assertions current` in `TargetAssertions` or in task verification that runs after writes, except the markup gate command defined in `markup_gate_planning`. Use selected target/final lint externally instead.
  </command_phase_rules>

<baseline_invariance>

- The markup gate runs `grace lint` in the default `--assertions current` mode, which evaluates `BaselineAssertions` of every active approved plan after every task, not only before the first write. Baseline must stay true for the whole change.
- Put into `BaselineAssertions` only invariants the change does not remove or rewrite: module ids, file existence, exported symbol names, `START_CONTRACT`/`START_BLOCK_` markers, and method names that survive the change.
- Never assert in baseline any text the change deletes or edits (old version literals, removed calls, values being replaced), and never assert `MustNotContain` on text the change adds. Express removal as `MustNotContain` and the new text as `MustContain` in `TargetAssertions`.
- Before approval, check every baseline `MustContain` against the plan's tasks: if any task edits or removes that text, move it to `TargetAssertions` as `MustNotContain`.
  </baseline_invariance>

<markup_gate_planning>

- The markup gate is these two commands, in this order:
  1. `grace lint --path PROJECT --failOn errors`
  2. `grace status --path PROJECT --json | jq -e '.observedDrift.unexplainedFiles | length == 0'`
- Every task that performs observed writes declares both as the first two leaf `<Command>` entries of that task's `<Verification>`, before acceptance tests, builds, typechecks, or other verification commands. `PROJECT` is the project root already used by the plan's other GRACE commands.
- Command 1 is the markup check. It fails on missing, duplicated, reversed, or unresolved `START_MODULE_CONTRACT`, `START_MODULE_MAP`, and `LINKS` markers in governed files, and on module-map parity breaks wherever the language has a bundled or runtime-backed analysis adapter.
- Command 2 is the scope check. It compares changed paths against the active approved `ObservedWriteScope`, covering added, modified, deleted, renamed, and untracked paths, and fails when any changed path is unexplained. `jq -e` turns that report into a real exit status.
- Prerequisites are the installed `grace` CLI and `jq`. Command 1 runs in default assertion mode without `--runCommands`: it is markup evidence, not assertion evidence, and it is the one permitted post-write `grace lint` invocation.
- Require each task handoff to quote both invocations with their actual output and exit status. The executor runs them immediately after the task's observed edits and stops before acceptance/tests when either exits nonzero.
  </markup_gate_planning>

<test_planning>

- Tests are banned in this project. Never plan a test, a test target, a coverage gate, or a test result as evidence, and never add one to close a verification gap.
- For every task, name in `AcceptanceCriteria` the observable contract it protects and the static or runtime gate that covers it: `make gate-backend`, `make gate-frontend`, `make gate-openapi` (API contract drift), `make gate-compose`, `grace lint`, or `grace status` drift.
- Where no existing gate can machine-check the contract, say so in the task and record the invariant as a review obligation. An honest "no gate covers this" beats a banned test.
  </test_planning>

<validation>
- Active-baseline preflight: `grace lint --path PROJECT --assertions current`
- Parallel safety: `grace lint --path PROJECT --parallel-preflight`
- Before approval, inspect every write task and reject the plan unless its first two verification commands are exactly the markup gate commands defined in `markup_gate_planning`.
- Reject the plan if any `BaselineAssertions` `MustContain` text is edited or removed by a planned task; baseline must remain valid for the whole change because the markup gate evaluates it after every task (see `baseline_invariance`).
- Before approval, check every task against `test_planning`, and revise the plan where a task plans a test, or where a task names no gate for the contract it changes.
- Recommend `grace status --path PROJECT --json` after approval.
</validation>

<hard_rules>
Do not implement code, silently approve a plan, overwrite an approved plan, or mutate current graph/verification artifacts while planning. Semantic anchors are canonical XML tags, never attributes.
</hard_rules>
</skill>

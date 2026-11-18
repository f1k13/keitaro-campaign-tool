---
name: grace-execute
description: Execute an approved GRACE 4 GraceChangePlan in sequential or parallel-safe mode with recovery-aware preflight and centralized durable apply.
---

<skill>
<preflight>
Require one active bundle with approved, identity-matched `spec.xml` and `plan.xml`. Approved plans are immutable. Read context, projections, assertions, scopes, task dependencies, and verification before editing. Reject phase-incompatible plans before writes: `MustPassCommand` must be leaf project evidence, and apart from the markup gate commands in execution rule 3, neither target assertions nor post-write task verification may invoke `--assertions current` or nest GRACE lifecycle commands. Reject a plan whose `BaselineAssertions` `MustContain` text is edited or removed by its own tasks: the default-mode markup gate evaluates active baselines after every task and would fail permanently. Supersede and replan before writes instead of editing an approved conflict in place.
</preflight>

<assertion_commands>

- Active-baseline preflight before observed writes: `grace lint --path PROJECT --assertions current`
- Selected baseline: `grace lint --path PROJECT --change C-ID --assertions baseline` (add `--runCommands` when the baseline declares `MustPassCommand`)
- Selected target without commands: `grace lint --path PROJECT --change C-ID --assertions target`
- Selected target with command evidence: `grace lint --path PROJECT --change C-ID --assertions target --runCommands`
- Final end-state validation: `grace lint --path PROJECT --change C-ID --assertions final` (add `--runCommands` when the target declares `MustPassCommand`)
- Parallel preflight: `grace lint --path PROJECT --parallel-preflight`
  </assertion_commands>

<mode_selection>
Wait for explicit `sequential` or `parallel-safe` choice. Parallel-safe requires the explicit preflight to pass. Workers never mutate approved plans; durable `.grace` changes are applied centrally after observed work verifies.
</mode_selection>

<recovery_decision_table>
| state | required action |
| clean-to-start | Run selected baseline, then execute tasks. |
| partial-observed-writes | Inspect the declared observed scope and ask whether to resume or revert. |
| durable-state-changed | Hard stop; supersede and replan. Approved assertions are immutable. |
| target-already-satisfied | Run final end-state validation, opted-in command evidence when declared, durable reconciliation, and ask for explicit apply confirmation. |
| unsafe-unknown-drift | Hard stop and report unexplained files. |
</recovery_decision_table>

<execution_rules>

1. Run the selected baseline before implementation, including explicit `--runCommands` when its assertions declare `MustPassCommand`.
2. Execute one dependency-ready task or one verified parallel-safe batch at a time. Hand each task to grace-worker when it is available while the controller runs the gates and keeps the evidence; execute a task directly only when its edit is a few lines or the user asked for a small direct fix, and name that exception.
3. **Markup gate (hard stop).** Immediately after each task's observed edits and before acceptance/tests, run the two markup gate commands declared by that task, in order: `grace lint --path PROJECT --failOn errors`, then `grace status --path PROJECT --json | jq -e '.observedDrift.unexplainedFiles | length == 0'`. The first fails on missing, duplicated, reversed, or unresolved `START_MODULE_CONTRACT`, `START_MODULE_MAP`, and `LINKS` markers in governed files, and on module-map parity breaks in analysed languages. The second fails when a changed path is not explained by the active approved `ObservedWriteScope`. It reads the working tree against `HEAD`, so leave observed writes uncommitted until the change is applied; committing mid-change hides those paths from the gate. If either command exits nonzero, stop: do not run task verification, close the task, apply durable state, or continue to the next task. Diagnose the reported failure, fix its cause within the approved `ObservedWriteScope`, and rerun both gate commands in order; repeat until both exit zero before resuming. The hard stop blocks progression, not corrective work.
4. Run each task's acceptance and verification immediately after both gate commands exit zero, and include both invocations with their actual output and exit status in the handoff.
5. Apply approved durable context, graph, and verification changes centrally.
6. Reconcile durable state, run leaf plan gates, then run selected `--assertions final` as the outermost lifecycle gate, including `--runCommands` when `MustPassCommand` is declared. Final mode performs full project lint, evaluates the selected target, keeps unrelated approved baselines active, and does not re-evaluate the selected plan's superseded baseline.
7. Ask for explicit apply confirmation after fresh end-state evidence passes. Before asking, run an independent grace-reviewer pass when the change touches code and grace-reviewer is available.
8. Only then set spec and plan to `applied` and archive the complete bundle.
9. Never edit approved assertions/scopes/tasks in place, bypass stale evidence, or continue through unknown drift.
   </execution_rules>
   </skill>

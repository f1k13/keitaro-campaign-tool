---
name: grace-ask
description: Answer questions about a GRACE 4 project by navigating .grace current-state artifacts and file-local semantic markup.
---

<skill>
<context_order>
1. `.grace/context/*.xml` for requirements, technology, principles, deployment, and UX constraints.
2. `.grace/graph/index.xml` then routed graph documents for `M-*` and `DF-*` ownership.
3. `.grace/verification/index.xml` then routed verification documents for `V-M-*` coverage.
4. `.grace/changes/active/C-*` for in-flight approved or draft work.
5. File-local `MODULE_CONTRACT`, `MODULE_MAP`, `LINKS:`, `START_CONTRACT`, and `START_BLOCK_` anchors.
</context_order>

<answer_rules>
- Cite the artifact or anchor that supports each important claim.
- Name the owning `M-*` module and its `V-M-*` entry in the answer itself, not only in the reading that produced it. A reader who sees the module and its verification entry knows where a change would land; a reader given only file paths has to rediscover that mapping.
- State a coverage finding against the declared set: name the `V-M-*` entry and say which of its `<TestFiles>` do or do not exercise the behavior. "The declared verification set for `V-M-EXAMPLE` does not cover this" is checkable and points at where the gap belongs; "no test covers this" is neither.
- Distinguish durable current state from active change intent.
- If legacy GRACE 3 docs are present, explain that they require `grace-migrate` and are not GRACE 4 truth.
- Report graph and verification facts only as the artifacts state them; where an artifact is silent, say so and name the safest next lookup.
</answer_rules>
</skill>

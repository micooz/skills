# Plan Mode

You work in 3 phases and should reason your way to a great implementation plan before finalizing it. A great plan is detailed enough to be handed to another engineer or agent and implemented immediately. It must be decision complete, where the implementer does not need to make any decisions.

## Mode rules (strict)

Stay in planning behavior until you produce a complete final plan.

If the user asks for execution while you are still planning, treat it as a request to plan the execution, not perform it.

## Execution vs. mutation during planning

You may explore and execute non-mutating actions that improve the plan. You must not perform mutating actions while planning.

### Allowed (non-mutating, plan-improving)

Actions that gather truth, reduce ambiguity, or validate feasibility without changing tracked state. Examples:

- Reading or searching files, configs, schemas, types, manifests, and docs
- Static analysis, inspection, and repo exploration
- Dry-run style commands when they do not edit tracked files
- Tests, builds, or checks that may write to caches or build artifacts so long as they do not edit tracked files

### Not allowed (mutating, plan-executing)

Actions that implement the plan or change tracked state. Examples:

- Editing or writing files
- Running formatters or linters that rewrite files
- Applying patches, migrations, or codegen that update tracked files
- Side-effectful commands whose purpose is to carry out the plan rather than refine it

When in doubt: if the action would reasonably be described as "doing the work" rather than "planning the work," do not do it.

## PHASE 1 - Ground in the environment

Begin by grounding yourself in the actual environment. Eliminate unknowns in the prompt by discovering facts through exploration. Resolve all questions that can be answered through inspection. Prefer evidence from the environment over assumptions whenever possible.

Before finalizing any plan, perform at least one targeted non-mutating exploration pass such as searching relevant files, inspecting likely entrypoints or configs, and confirming the current implementation shape.

## PHASE 2 - Intent resolution

Infer the user's likely goal, success criteria, audience, scope boundaries, constraints, current state, and key tradeoffs from the available context.

Do not stop to ask for confirmation. When intent is under-specified, choose the most defensible interpretation and document it as an assumption.

## PHASE 3 - Implementation resolution

Once intent is stable, continue until the spec is decision complete: approach, interfaces, data flow, edge cases, failure modes, testing, acceptance criteria, rollout concerns, and compatibility constraints.

Do not leave implementation choices unresolved. If multiple viable approaches exist for a specific action, present them together inline under that action and mark one as recommended.

## Module planning workflow

Follow the shared semantic model and artifact contracts in `SKILL.md` for requirement preprocessing, requirement-item identity, module lineage, dependency layering, checklist paths, and state-file expectations.

Within that shared contract, plan mode must:

1. extract implementation-bearing modules from the latest requirement source
2. derive dependency layering before classification or subagent spawning
3. classify each module into exactly one action: `new-plan`, `revise-plan`, `obsolete-plan`, or `no-op`
4. draft or revise the affected module plans
5. refresh `checklist.md`
6. refresh `plans/.state.json` after all affected modules are processed

### Module extraction and classification

Use these rules:

- Default to splitting by implementation units and dependency boundaries, not by repository package structure and not mechanically by requirement headings.
- If the source is plain text with no reliable headings, derive a concise module list from the requirement content and use feature boundaries, workflows, deliverables, prerequisite relationships, and requirement-item boundaries as extraction inputs.
- Avoid generic module names like `misc`, `other`, or `supporting-work`.
- If a new requirement item describes a new owner-level deliverable or dependency boundary, create a new module lineage for it.
- If a new requirement item only adds constraints, acceptance detail, or incremental scope to an existing module lineage, revise that lineage instead of creating a second base module.
- Removing a requirement item should produce `obsolete-plan` only when that item was the last active requirement item mapped to the module lineage; otherwise revise the surviving lineage.
- When no requirement source is available, allow review-driven revisions only.
- Comment-only edits in the requirement source must not trigger `revise-plan`.

### Review note handling

Treat review notes from the latest plan lineage as input constraints only.

Use these rules:

- Review detection is only meaningful inside `plans/*.md`.
- Treat any HTML comment outside fenced code blocks in plan files as a review note.
- If review content in user comments conflicts with the original requirement document, treat the review content as the latest authoritative instruction.
- Do not preserve HTML comments in final plan output.
- If the input material includes both requirement changes and review notes for the same module, merge both inputs into a single revised plan instead of producing multiple competing outputs.
- If a module disappeared from the latest requirement source, the output plan should become a retirement-oriented or obsolete plan rather than silently skipping that module.

### Checklist refresh

Generate or refresh `checklist.md` during every successful `plan` run.

Use these rules:

- Build the checklist from the latest requirement source plus authoritative review notes from the latest plan lineage.
- Treat review notes as authoritative checklist inputs only when they clarify, correct, add, remove, or sharpen requirement scope or acceptance expectations.
- Organize checklist sections by requirement topic, user-visible outcome, or reviewer-facing acceptance area rather than by dependency layer, module order, or raw requirement heading order.
- Module lineage and dependency metadata may inform wording disambiguation, but they must not become the primary checklist structure.
- First regenerate the checklist content from current authoritative inputs, then optionally restore prior checked states from the previous `checklist.md` only for safely matched unchanged items.
- Use Markdown headings plus actionable checklist items such as `- [] ...` or `- [x] ...`, with no space inside `[]`.
- Prefer verifiable acceptance outcomes and reviewer-observable results, not implementation steps, execution queues, agent work breakdowns, or narrative summaries.
- Do not rewrite the checklist into a dependency-sorted implementation task list.
- Preserve `[x]` only for safe one-to-one matches between old and new checklist items.
- Prefer the strongest available identity match first, such as requirement item identity, module lineage, and normalized checklist text.
- Treat pure reordering, heading movement, and non-semantic formatting-only rewrites as eligible for `[x]` preservation when the match is still safe and one-to-one.
- Do not preserve `[x]` for items whose resolved acceptance intent changed, including authoritative review-driven rewrites, requirement scope changes, item splits, item merges, unsafe rename cases, or ambiguous matches.
- If prior checklist content cannot be parsed safely, still refresh the new checklist and report that some or all prior checked states could not be preserved.
- If the source is a plan file or `plans/` directory, resolve the latest readable requirement source from `plans/.state.json` before refreshing the checklist.
- If a requirement source cannot be reconstructed safely, allow review-driven plan revisions to proceed but report that `checklist.md` could not be refreshed.

### Planning subagents and assembly

Spawn one planning subagent per affected module after locking the module list, dependency graph, and action.

Use these rules:

- Prefer read-only analysis subagents for planning work.
- Use a general-purpose subagent only if a dedicated read-only analysis role is unavailable and the subagent can still stay read-only.
- Planning subagents must not edit files.
- Pass this document's requirements through in each planning subagent prompt and instruct the subagent to follow this contract for its module output.
- Run planning subagents in parallel only within the same dependency layer.
- Ask each planning subagent to return plain Markdown module-plan draft content that is implementation-ready under this contract.
- Require each planning subagent draft to cover affected code areas, interfaces, dependencies, parallelism notes, risks, tests, and explicit assumptions.
- Resolve cross-module dependencies so terminology and shared changes stay consistent.
- Confirm one clear owner for each shared interface, schema, migration, or infrastructure change.
- Order final module output according to dependency layers rather than requirement heading order.
- State explicitly when a module is blocked by another module or can run in parallel after prerequisites.

## Unknowns and defaults

Treat unknowns in two categories:

1. Discoverable facts: resolve them through exploration whenever possible.
2. Preferences or tradeoffs that cannot be discovered: select a recommended default and continue.

Use assumptions to unblock planning, not to avoid exploration. Every important assumption should be explicit in the final plan.

## Finalization rule

Only output the final plan when it is implementation-ready.

Write the official plan as plain Markdown content only.

The final plan must be concise by default, plan-only, and include:

- A clear title
- A brief summary
- Key actions that can be executed without further human confirmation
- Important changes or additions to public APIs, interfaces, or types
- Test cases and scenarios
- Explicit assumptions and defaults chosen

The final plan output must not contain HTML comments, reviewer annotations, wrapper tags, or any other non-plan markers. If review comments were present in the input plan file, absorb their intent into the revised plan and remove the comments from the output entirely.

When possible, prefer a compact structure with 4-6 short sections, usually: Summary, Key Changes, Test Plan, and Assumptions.

For revision outputs, use a patch-first update strategy. Preserve unchanged valid sections, headings, order, and untouched text whenever possible, and rewrite only the annotated action blocks plus directly affected supporting content.

## Action option requirements

The recommended option for an action is the execution baseline. It must:

- Be specific enough to implement directly
- Explain why it is preferred under the current constraints
- Avoid leaving unresolved design choices to the implementer

For obsolete or retirement-oriented plans, the recommended option must explain what work stops, what work remains necessary for safe retirement, and how adjacent modules should adapt.

When a specific action has multiple viable options:

- Prefix the action line with `【⚠ Decision Required ⚠】`.
- Present them together under that action instead of separating recommendation and alternatives into different sections.
- Label the options as `a.` `b.` `c.`.
- Mark the preferred option with `(Recommended)`, e,g. `a. (Recommended) ...`.
- Keep each option short but comparative: include the approach, the main benefit, and the main tradeoff.

If an action has only one reasonable path, write it directly without inventing extra options.

## Writing guidance

Prefer grouped implementation bullets by subsystem or behavior over file-by-file inventories. Mention files only when needed to disambiguate a non-obvious change, and avoid naming more than 3 paths unless extra specificity is necessary to prevent mistakes.

Keep bullets short and avoid explanatory sub-bullets unless they are needed to prevent ambiguity. Prefer the minimum detail needed for implementation safety, not exhaustive coverage. Compress related changes into a few high-signal bullets and omit repeated invariants, unaffected behavior, and irrelevant detail unless they are necessary to prevent a likely implementation mistake.

When revising an existing plan:

- Default to section-level preservation rather than whole-document rewrite.
- Keep unchanged sections verbatim when they are still valid.
- Allow targeted ripple edits to summary, tests, assumptions, and cross-references only when needed to keep the document consistent.
- If the latest requirement source changed outside the annotated area, expand the rewrite only to the impacted section or related action group by default.

Do not ask whether to proceed. If important preferences remain unknown, proceed with the recommended default and document it in Assumptions and Alternatives Considered.

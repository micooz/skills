---
name: batch-plan-execute
description: Use when the user wants AI to turn a requirement text, requirement document, and existing reviewed plan files into dependency-ordered implementation plans, a consolidated `checklist.md`, and, only after an explicit execution command, implement those plans with subagents in parallel where safe and in sequence where required.
---

# Batch Plan Execute

Use this skill when the task is to create, revise, retire, execute, or inspect module plans and the derived `checklist.md` based on a requirement source and the current `plans/` directory state.

This skill currently has these explicit modes:

- `plan`: generate or revise implementation-ready plans and refresh `checklist.md`
- `execute`: implement already-reviewed plans

This skill can do the following things:

- Accepts requirement text from chat, a requirement file such as `requirements.md`, or an existing plan file or `plans/` directory.
- Reconstructs the current planning state from the latest requirement source, existing plan files, and a hidden state file.
- Detects mixed changes per module: new requirements, changed requirements, removed requirements, and review notes.
- Builds dependency-aware module or workstream plans that reflect parallelizable and serial work.
- Generates a consolidated `checklist.md` from the latest requirement source plus authoritative review notes.
- Executes approved plans with subagents only after an explicit execution command from the user.

## Input Handling

Choose the primary input in this order:

1. An explicit plan file path or `plans/` directory path mentioned by the user.
2. An explicit requirement file path mentioned by the user.
3. A file or document already attached in the task context.
4. The requirement text written directly in the chat.

Use these rules:

- If a plan file path is provided, treat that plan lineage as the primary starting point and inspect the sibling `plans/` directory.
- If a `plans/` directory path is provided, inspect only plan files and the state file inside that directory.
- If a requirement file path is provided, read it directly and treat it as the latest requirement source.
- If the input is raw chat text, treat the full user text as the latest requirement source.
- If both a requirement source and a `plans/` directory are available, always use both.

Fail immediately if any referenced file or directory does not exist or is not readable.

## Output Language

Use these rules:

- Match all user-visible output language to the dominant language of the latest requirement source.
- If no requirement source exists, match the dominant language of the user's current-turn input.
- If the user explicitly asks for translation or a specific output language, follow that instead.

## Mode Selection

Default to `plan` mode.

Switch to `execute` mode only when the user explicitly issues an execution command in the current turn.

Examples that DO resolve to `execute` mode:

- `开始执行`
- `按这个方案实现`
- `去改代码`
- `直接落地`
- `implement now`
- `apply the plan`

Examples that DO NOT change mode from the default `plan` behavior:

- `LGTM`
- `OK`
- `继续`
- `按这个方向`
- `review 过了`
- any approval that confirms the plan but does not explicitly ask to start implementation

Use these rules:

- Review approval is not execution approval.
- If the user is ambiguous, stay in `plan` mode and either refine the execution plan or ask for a clearer execution command.
- Never infer execution intent from momentum, optimism, or lack of objections.

## Output Location And Naming

Write plan files into a `plans/` directory:

- If the source is a requirement file, use a `plans/` folder next to that file.
- If the source is a plan file or `plans/` directory, keep writing into that same `plans/` directory.
- If the source is raw chat text, use `<cwd>/plans/`.

Create the `plans/` directory if it does not exist.

Base plan files use this format:

- `<module-slug>.md`

Revision plan files use this format:

- `<module-slug>.rev-<n>.md`

The derived checklist file must be:

- `checklist.md`

The hidden state file must be:

- `.state.json`

Use these naming rules:

- `new-plan` may create a base file if the module has no prior lineage.
- `revise-plan` and `obsolete-plan` must always write a new `rev` file.
- `no-op` must not write a new plan file.
- Do not overwrite an existing file silently.
- Plan slugs should follow implementation ownership, not requirement heading text, when the two differ.
- A new standalone `---`-delimited requirement segment may create a new base file only when it resolves to a new module lineage rather than a revision of an existing lineage.
- If a new `---`-delimited requirement segment only expands an existing module lineage, write a new `rev` file for that lineage instead of creating a second base file.
- Slugs derived from `---`-delimited requirement segments must still describe the implementation owner-level deliverable, not the raw segment order or divider label.
- If the latest requirement source is a readable file, write `checklist.md` next to that requirement file instead of inside `plans/`.
- If no readable requirement file exists, fall back to writing `checklist.md` inside the active `plans/` directory.
- Always overwrite the resolved `checklist.md` path in place when it can be refreshed safely.
- `checklist.md` is a derived snapshot, not a plan lineage artifact and not an execution target.

## State File

Maintain `plans/.state.json` as the planning baseline.

The state file must contain at least:

- `requirement_source`
- `requirement_hash`
- `run_at`
- `requirement_items`
- `modules`

Each requirement item state object must contain at least:

- `item_id`
- `source_kind`
- `source_order`
- `source_excerpt_hash`
- `body_hash_without_comments`
- `mapped_module_slug`

Each module state object must contain at least:

- `slug`
- `title`
- `status`
- `source_excerpt_hash`
- `body_hash_without_heading`
- `requirement_item_ids`
- `latest_plan_file`
- `latest_rev`
- `last_action`

Status values must be explicit:

- `active`
- `obsolete`

Use these rules:

- The state file describes planning lineage only.
- `requirement_items` track extraction-time requirement identities, including standalone `---`-delimited segments, before they are merged into final module boundaries.
- A new standalone `---`-delimited requirement segment must produce a new requirement item identity even when it is later merged into an existing module lineage.
- Do not treat the state file as permission to execute.
- If the state file is missing, bootstrap from the latest requirement source and the existing plan files instead of failing.
- Bootstrap must reconstruct both requirement items and module mappings using the same divider and comment-preprocessing rules as normal plan mode.

## Plan Mode

Use [docs/plan.md](./docs/plan.md) as the detailed plan-writing contract.

### Module Extraction

Default to splitting by implementation units and dependency boundaries, not by repository package structure and not mechanically by requirement headings.

Before extracting modules or computing any requirement hashes, preprocess the latest requirement source in this order:

1. remove HTML comments outside fenced code blocks
2. ignore Markdown structure inside fenced code blocks
3. exclude document-frontmatter `---` delimiters from requirement extraction
4. detect standalone `---` lines in the remaining requirement body as requirement-item dividers only when they are outside fenced code blocks, outside removed comments, and surrounded by non-empty requirement content

Use these rules:

- Treat commented requirement content as nonexistent.
- Treat each standalone `---`-delimited body segment as a distinct requirement item candidate before module mapping.
- Start from requirement sections and `---`-delimited requirement items only as extraction aids, not as the final module boundary.
- A newly added standalone `---`-delimited segment in the latest requirement source must be treated as a new requirement item even if it later maps to an existing module lineage.
- Treat meta sections such as background, goals, scope, non-goals, assumptions, rollout, acceptance criteria, and non-functional requirements as global constraints, not standalone modules.
- Merge requirement slices that land on the same implementation path, shared code surface, or same owner-level deliverable.
- Split a section or divider-delimited item only when it clearly describes independent deliverables or a strict implementation sequence such as foundation work before feature work.
- Prefer module boundaries that match functional ownership, shared interface ownership, migration boundaries, or deployment boundaries.
- If a new `---`-delimited requirement item describes a new owner-level deliverable or dependency boundary, create a new module lineage for it.
- If a new `---`-delimited requirement item only adds constraints, acceptance detail, or incremental scope to an existing module lineage, merge it into that lineage instead of creating a second base module.
- Do not create overlapping modules that both own the same shared change.
- Fail loudly if no implementation-bearing modules can be extracted or if shared ownership cannot be assigned clearly.

If the source is plain text with no reliable headings:

- derive a concise module list from the requirement content
- use feature boundaries, workflows, deliverables, prerequisite relationships, and standalone `---`-delimited items as module extraction inputs
- avoid generic module names like `misc`, `other`, or `supporting-work`

### Dependency And Parallelism Modeling

After extracting candidate modules, derive an explicit dependency graph before classification or subagent spawning.

Use these rules:

- Classify each module as `foundation`, `feature`, or `follow-on`.
- Record `depends_on`, `blocks`, `parallelizable_with`, and `shared_change_owner`.
- Prefer parallel modules only when they do not require the same shared code ownership in the same phase.
- Prefer serial sequencing when one module changes contracts, schemas, migrations, or shared utilities that another module consumes.
- If the implementation is `A then B`, model that directly instead of forcing both into one peer list.
- Do not infer fake parallelism. Sequence conservatively if safe ordering is unclear.

### Review Detection And Lineage

Review detection is only meaningful inside `plans/*.md`.

Use these rules:

- Treat any HTML comment outside fenced code blocks as a review note.
- If review content in user comments conflicts with the original requirement document, treat the review content as the latest authoritative instruction.
- Do not preserve HTML comments in final plan output.
- Resolve the latest lineage artifact by highest `rev`, otherwise latest base file.
- Prefer slug matches first.
- Allow rename matching only for safe one-to-one matches on `body_hash_without_heading`.
- If rename matching is ambiguous, do not guess.

### Checklist Generation

Generate or refresh `checklist.md` during every successful `plan` run.

Use these rules:

- Build the checklist from the latest requirement source plus authoritative review notes from the latest plan lineage.
- Apply the same requirement preprocessing used for module extraction before deriving checklist items.
- Treat standalone `---`-delimited requirement segments as distinct requirement items during checklist derivation, using the same exclusion rules for frontmatter, comments, and fenced code blocks.
- Treat review comments as authoritative when they conflict with the original requirement document.
- Never preserve raw HTML comments in `checklist.md`; only preserve their resolved intent.
- Organize checklist sections by dependency layer and module order, not by raw requirement heading order.
- Use Markdown headings plus actionable unchecked items such as `- [] ...`, no space inside of `[]`.
- Prefer verifiable implementation or acceptance outcomes, not narrative summaries.
- Empty divider segments, comment-only segments, and formatting-only divider changes must not create checklist entries.
- If the latest requirement source is a readable file, write `checklist.md` next to that requirement file.
- If no readable requirement file exists, write `checklist.md` inside the active `plans/` directory.
- If the source is a plan file or `plans/` directory, resolve the latest readable requirement source from `plans/.state.json` before refreshing the checklist.
- If a requirement source cannot be reconstructed safely, allow review-driven plan revisions to proceed but report that `checklist.md` could not be refreshed.

### Mixed-Mode Classification

Determine action per module, not once for the whole run.

Classify each module into exactly one action:

- `new-plan`
- `revise-plan`
- `obsolete-plan`
- `no-op`

Use these defaults:

- Merge requirement changes and review notes into one `revise-plan`.
- A newly added standalone `---`-delimited requirement segment must classify as `new-plan` when it maps to no existing module lineage.
- A newly added standalone `---`-delimited requirement segment must classify as `revise-plan` when it safely expands an existing module lineage.
- Removing a standalone `---`-delimited requirement item should produce `obsolete-plan` only when that item was the last active requirement item mapped to the module lineage; otherwise revise the surviving lineage.
- Generate an `obsolete-plan` revision instead of silently dropping removed modules.
- When no requirement source is available, allow review-driven revisions only.
- Comment-only edits in the requirement source must not trigger `revise-plan`.
- Empty divider segments, comment-only divider segments, and formatting-only divider changes must not trigger `new-plan` or `revise-plan`.

### Plan Subagents

Spawn one planning subagent per affected module after locking the module list, dependency graph, and action.

Use these rules:

- Prefer read-only analysis subagents for planning work.
- Use a general-purpose subagent only if a dedicated read-only analysis role is unavailable and the subagent can still stay read-only.
- Planning subagents must not edit files.
- Pass [docs/plan.md](./docs/plan.md) requirements through in each planning subagent prompt and instruct the subagent to follow that contract for its module output.
- Run planning subagents in parallel only within the same dependency layer.
- Ask each planning subagent to return plain Markdown module-plan draft content that is implementation-ready under the `docs/plan.md` contract.
- Require each planning subagent draft to cover affected code areas, interfaces, dependencies, parallelism notes, risks, tests, and explicit assumptions.

### Plan Assembly

The main agent owns final plan quality, plan file output, and state file updates.

Use these rules:

- Resolve cross-module dependencies so terminology and shared changes stay consistent.
- Confirm one clear owner for each shared interface, schema, migration, or infrastructure change.
- Order final module output according to dependency layers rather than requirement heading order.
- State explicitly when a module is blocked by another module or can run in parallel after prerequisites.
- Refresh `checklist.md` after module plans are assembled and before refreshing the state file.
- Refresh `plans/.state.json` only after all affected modules are processed.

## Execute Mode

Use [docs/execute.md](./docs/execute.md) as the detailed execution contract.

### Execution Preconditions

Fail immediately if any of these is true:

- no target plan file or `plans/` directory can be resolved
- the latest target plan artifact still contains unresolved review comments
- the selected plan set does not define dependency layering, upstream prerequisites, shared-change ownership, or write scopes clearly enough for direct dispatch
- shared-change ownership is ambiguous
- dependency cycles cannot be justified as a merged module

### Execution Rules

After the gate and preconditions are satisfied:

- use `docs/execute.md` for target resolution, preflight, worker dispatch, integration, verification, and completion
- execute the latest reviewed artifact for each selected module lineage
- dispatch directly from the approved plan boundaries and dependency metadata instead of re-grounding the repository to redefine scope
- respect the dependency graph recorded in the latest plan set before dispatch
- spawn one subagent per ready module unless multiple modules must be merged for safe shared-change ownership or an irreducible dependency cycle

## Failure Rules

Stop and report the problem instead of generating weak output when:

- the requirement file, plan file, or plans directory is missing or unreadable
- module extraction fails for a required requirement source
- a plan would be mostly speculation with no meaningful codebase tie-in
- multiple latest lineage candidates exist for one module and the ordering cannot be resolved safely
- rename matching is ambiguous and cannot be reduced to a safe one-to-one mapping
- shared changes or dependency ownership cannot be assigned to one clear module or workstream
- the dependency graph contains cycles that cannot be justified as a single merged module
- the state file exists but is malformed and cannot be safely reconstructed from visible artifacts

Do not emit empty plan files, summary-only files, or a single aggregate plan when the task requires per-module outputs.

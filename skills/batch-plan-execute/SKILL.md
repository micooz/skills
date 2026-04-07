---
name: batch-plan-execute
description: Use when the user wants AI to turn a requirement text, requirement document, and existing reviewed plan files into dependency-ordered implementation plans, a consolidated `checklist.md`, and, only after an explicit execution command, implement those plans with subagents in parallel where safe and in sequence where required.
---

# Batch Plan Execute

Use this skill when the task is to create, revise, retire, execute, or inspect module plans and the derived `checklist.md` based on a requirement source and the current `plans/` directory state.

This skill has two explicit modes:

- `plan`: generate or revise implementation-ready plans and refresh `checklist.md`
- `execute`: implement already-reviewed plans

This skill can:

- accept requirement text from chat, a requirement file such as `requirements.md`, or an existing plan file or `plans/` directory
- reconstruct the current planning state from the latest requirement source, existing plan files, and a hidden state file
- detect mixed changes per module: new requirements, changed requirements, removed requirements, and review notes
- build dependency-aware module or workstream plans that reflect serial and parallel work safely
- generate a consolidated `checklist.md` from the latest requirement source plus authoritative review notes
- execute approved plans with subagents only after an explicit execution command from the user

## Inputs And Resolution

### Primary Input Resolution

Choose the primary input in this order:

1. an explicit plan file path or `plans/` directory path mentioned by the user
2. an explicit requirement file path mentioned by the user
3. a file or document already attached in the task context
4. the requirement text written directly in the chat

Use these rules:

- If a plan file path is provided, treat that plan lineage as the primary starting point and inspect the sibling `plans/` directory.
- If a `plans/` directory path is provided, inspect only plan files and the state file inside that directory.
- If a requirement file path is provided, read it directly and treat it as the latest requirement source.
- If the input is raw chat text, treat the full user text as the latest requirement source.
- If both a requirement source and a `plans/` directory are available, always use both.
- Fail immediately if any referenced file or directory does not exist or is not readable.

### Output Language Resolution

Use these rules:

- Match all user-visible output language to the dominant language of the latest requirement source.
- If no requirement source exists, match the dominant language of the user's current-turn input.
- If the user explicitly asks for translation or a specific output language, follow that instead.

## Mode Routing

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

## Shared Semantic Model

### Requirement Preprocessing

Before extracting requirements, computing requirement-derived hashes, deriving checklist items, or interpreting review notes, preprocess the latest requirement source in this order:

1. remove HTML comments outside fenced code blocks
2. ignore Markdown structure inside fenced code blocks
3. exclude document-frontmatter `---` delimiters from requirement segmentation
4. detect standalone `---` lines in the remaining requirement body as requirement-item dividers only when they are outside fenced code blocks, outside removed comments, and surrounded by non-empty requirement content

Use these rules:

- Treat commented requirement content as nonexistent.
- HTML comments inside fenced code blocks are not review notes.
- Review comments are only meaningful inside `plans/*.md`; requirement sources use the same comment-boundary semantics for preprocessing only.
- Empty divider segments, comment-only divider segments, and formatting-only divider changes must not create semantic requirement changes.

### Requirement Item Identity And Segmentation

Use these rules:

- Treat each standalone `---`-delimited body segment as a distinct requirement item candidate before module mapping.
- Start from requirement sections and `---`-delimited requirement items only as extraction aids, not as final module boundaries.
- A new standalone `---`-delimited requirement segment must produce a new requirement item identity even when it is later merged into an existing module lineage.
- Requirement item state must preserve extraction-time identity before any later module merge, including `item_id`, `source_kind`, `source_order`, `source_excerpt_hash`, `body_hash_without_comments`, and `mapped_module_slug`.
- Meta sections such as background, goals, scope, non-goals, assumptions, rollout, acceptance criteria, and non-functional requirements are global constraints unless they clearly describe implementation-bearing work.

### Module Lineage And Ownership

Use these rules:

- Module boundaries should follow implementation ownership, shared code surface, migration boundaries, deployment boundaries, and owner-level deliverables rather than raw heading order.
- Plan slugs should follow implementation ownership, not requirement heading text, when the two differ.
- Merge requirement slices that land on the same implementation path, shared code surface, or owner-level deliverable.
- Split only when the source clearly describes independent deliverables or strict prerequisite sequencing.
- Do not create overlapping modules that both own the same shared change.
- If a shared change is needed by multiple modules, assign one clear owner module lineage.
- Resolve latest lineage artifacts by highest `rev`, otherwise latest base file.
- Prefer slug matches first.
- Allow rename matching only for safe one-to-one matches on `body_hash_without_heading`.
- If rename matching is ambiguous, do not guess.

### Dependency Layering And Parallelism

After extracting candidate modules, derive an explicit dependency graph before classification or subagent spawning.

Use these rules:

- Classify each module as `foundation`, `feature`, or `follow-on`.
- Record `depends_on`, `blocks`, `parallelizable_with`, and `shared_change_owner`.
- Prefer parallel modules only when they do not require the same shared code ownership in the same phase.
- Prefer serial sequencing when one module changes contracts, schemas, migrations, shared utilities, or infrastructure that another module consumes.
- If the implementation is `A then B`, model that directly instead of forcing both into one peer list.
- Do not infer fake parallelism. Sequence conservatively if safe ordering is unclear.

## Artifact Model And File Contracts

### Plan File Lineage

Write plan files into a `plans/` directory:

- If the source is a requirement file, use a `plans/` folder next to that file.
- If the source is a plan file or `plans/` directory, keep writing into that same `plans/` directory.
- If the source is raw chat text, use `<cwd>/plans/`.

Create the `plans/` directory if it does not exist.

Base plan files use this format:

- `<module-slug>.md`

Revision plan files use this format:

- `<module-slug>.rev-<n>.md`

Use these naming rules:

- `new-plan` may create a base file if the module has no prior lineage.
- `revise-plan` and `obsolete-plan` must always write a new `rev` file.
- `no-op` must not write a new plan file.
- Do not overwrite an existing file silently.
- A new standalone `---`-delimited requirement segment may create a new base file only when it resolves to a new module lineage rather than a revision of an existing lineage.
- If a new `---`-delimited requirement segment only expands an existing module lineage, write a new `rev` file for that lineage instead of creating a second base file.
- Slugs derived from `---`-delimited requirement segments must still describe the implementation owner-level deliverable, not the raw segment order or divider label.

### Checklist Contract

The derived checklist file must be:

- `checklist.md`

Use these rules:

- If the latest requirement source is a readable file, write `checklist.md` next to that requirement file instead of inside `plans/`.
- If no readable requirement file exists, fall back to writing `checklist.md` inside the active `plans/` directory.
- Always overwrite the resolved `checklist.md` path in place when it can be refreshed safely.
- `checklist.md` is a derived acceptance snapshot based on the latest requirement source and authoritative review notes.
- It exists to help humans verify whether the requested outcomes and acceptance expectations have been satisfied.
- It is not a plan lineage artifact, not an execution target, and not an implementation task list.
- Review notes may refine or correct checklist content only when they change the authoritative requirement or acceptance intent.
- If an earlier `checklist.md` exists, treat it only as an optional source of prior checkbox state for safely matched unchanged items, never as the source of truth for checklist content.

### State File Contract

The hidden state file must be:

- `.state.json`

Maintain `plans/.state.json` as the planning baseline.

The state file must contain at least:

- `requirement_source`
- `requirement_hash`
- `run_at`
- `requirement_items`
- `modules`

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
- Do not treat the state file as permission to execute.
- If the state file is missing, bootstrap from the latest requirement source and the existing plan files instead of failing.
- Bootstrap must reconstruct both requirement items and module mappings using the same shared semantic model as normal plan mode.
- If the state file exists but is malformed and cannot be safely reconstructed from visible artifacts, fail.

## Plan Mode

Use [docs/plan.md](./docs/plan.md) as the detailed plan-writing and plan-refresh contract.

Plan mode is responsible for:

- extracting implementation-bearing modules from the latest requirement source under the shared semantic model
- classifying each module into exactly one action: `new-plan`, `revise-plan`, `obsolete-plan`, or `no-op`
- producing implementation-ready module plans
- refreshing `checklist.md`
- refreshing `plans/.state.json` after all affected modules are processed

Use these rules:

- Treat authoritative review notes from the latest plan lineage as input constraints for plan revisions.
- Merge requirement changes and review notes into one revised module plan when both affect the same lineage.
- Generate or refresh `checklist.md` during every successful `plan` run.
- Keep detailed module extraction, checklist refresh, subagent planning, and plan assembly behavior in `docs/plan.md` rather than duplicating it here.

## Execute Mode

Use [docs/execute.md](./docs/execute.md) as the detailed execution contract.

Execute mode is responsible for:

- resolving the target plan file or `plans/` directory
- selecting the latest reviewed artifact for each chosen module lineage
- dispatching execution directly from approved plan boundaries and dependency metadata
- validating the implemented change before reporting completion

Use these rules:

- Execute only after an explicit execution command in the current turn.
- Execute the latest reviewed artifact for each selected module lineage.
- Fail immediately if the latest target artifact still contains unresolved review comments.
- Treat approved plans as the execution boundary source of truth. Do not re-scope modules, re-derive write ownership, or re-plan dependency layering during execute mode.
- Keep target resolution, preflight, worker dispatch, integration, verification, and completion details in `docs/execute.md` rather than duplicating them here.

## Failure Conditions

Stop and report the problem instead of generating weak output when:

- the requirement file, plan file, or `plans/` directory is missing or unreadable
- module extraction fails for a required requirement source
- a plan would be mostly speculation with no meaningful codebase tie-in
- multiple latest lineage candidates exist for one module and the ordering cannot be resolved safely
- rename matching is ambiguous and cannot be reduced to a safe one-to-one mapping
- shared changes or dependency ownership cannot be assigned to one clear module or workstream
- the dependency graph contains cycles that cannot be justified as a single merged module
- the state file exists but is malformed and cannot be safely reconstructed from visible artifacts

Do not emit empty plan files, summary-only files, or a single aggregate plan when the task requires per-module outputs.

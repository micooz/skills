---
name: deslop
description: 'Reduce redundancy in comments, docstrings, and docs: comments that restate code, historical or provenance notes, commented-out code, stale or contradictory text, over-explanation, and finished plans written as current guidance. Use after writing or reviewing code or docs, before committing a diff, or on requests such as 清理冗余注释、去 slop、历史注释、过时注释、过度解释、精简文档. Edits only comments and prose, never executable code. Defaults to the current diff; it does not sweep an untouched repository unless asked.'
---

# Deslop

Remove redundancy from comments and docs without touching behavior. Slop is text a careful human author would not have written: it repeats what the code already shows, records history that Git owns, or describes a state that is no longer true.

This skill edits comments, docstrings, and prose only. Unused symbols, `any` casts, nesting, and style belong to the project's linter, type checker, and formatter; do not fix them here. If you notice dead or suspicious code, mention it in the report and leave it.

## Target Scope

Coverage applies to both code comments and documentation prose.

Default target: files in the current diff (uncommitted changes plus commits ahead of the default branch), plus any paths the user names. Gather them with `git status --short` and a diff against the default branch (fallback to `git diff HEAD` if upstream or default branch cannot be determined).

- If the diff includes changes this session did not make, treat them as in scope but keep edits to comments and prose that the diff touched or sits next to. Do not rewrite untouched parts of those files.
- If the user specifies explicit files, directories, or patterns, inspect those specified targets directly (whether or not they are part of a git diff).
- In non-git environments, shallow clones, or dirty trees without upstream: inspect user-specified paths directly; if no path is given, check files touched in the current session or ask for target paths instead of failing silently.
- Widen to whole directories or the repository only when the user asks.
- Never edit files outside the set; list them in the report instead.
- If the set is empty, say so and stop.

## Comments

Remove:

- Comments that restate the next line (`// Increment counter`, `// Return the result`).
- Internal provenance and personal commit history: dates of edits, author names, `@author`, "was X, now Y", "previously", "added in the March refactor". (Distinguish from third-party attribution and compliance notes below).
- Commented-out code. Exception: a comment that records a deliberate off-switch ("paused while upstream is down") stays; report it.
- Code samples inside comments that duplicate tests or docs.
- Comments that contradict the code. The code is the truth; fix or delete the comment. If the code itself looks wrong, report it without changing it.
- Banner, divider, and section-header comments that only repeat the structure visible in the file.

Shorten, do not delete:

- Multi-paragraph comments around a single non-obvious decision: keep the reason, drop the narration.

Keep, always:

- Why a non-obvious decision was made: algorithm choice, performance tradeoff, security or policy constraint, workaround for an external system's quirk.
- Stage or step navigation signposts in long functions or complex state machines (`// Step 1: parse header`, `// Phase 2: handshake`), provided they chunk distinct logical stages rather than restate trivial single lines.
- Spec and requirement references (`per ADR-003`, `RFC 9457`, ticket ids). They are references, not history.
- Legal, license, and third-party attribution / provenance (`Ported from...`, `Adapted from...`, original author attribution or paper citations). These are compliance and source credits, not git history slop.
- Measured evidence with its conditions (environment, version, date, sample size). Here the date is part of the claim.
- Diagnostic notes: counters, timing, stall or retry explanations, failure classification.
- Directive comments that tools read: `eslint-disable`, `@ts-expect-error`, `@ts-ignore`, `noqa`, `# type:`, `#region`, `// prettier-ignore`, `SAFETY:` blocks, license headers, shebangs, build or codegen markers.
- `TODO` and `FIXME`. If one has no concrete action, report it rather than deleting it.

Docstrings: make documented parameters and return values agree with the signature. For exported/public API items, preserve docstrings even if brief when they serve IDE hover/tooltips or documentation generators (TypeDoc, Sphinx, rustdoc); only delete completely vacuous docstrings on private or unexported helpers that purely echo the identifier name without adding context. Keep ones that state contracts, units, error behavior, or examples that the signature cannot express.

## Docs

Applies to README, guides, design notes, and similar prose.

Remove or rewrite:

- Completed checklists, phase logs, implementation narratives, and verification transcripts presented as current guidance.
- Executed plans still written as future intent.
- Statements that contradict each other within one document; resolve toward the current code.
- References to renamed or deleted paths, commands, and configuration keys; verify against the tree first.
- Inventory text the tree already shows: file counts, sizes, timestamps.
- Filler and marketing tone: restated headings, "In this section we will...", unearned superlatives, emoji used as decoration.

Keep:

- Decision records: ADRs and rationale for a chosen design, including why alternatives were rejected. These explain the present, not the past. Remove rejected-option analysis only from documents that are meant to be pure usage guidance.
- Anything the user marked as a draft or protected.

Documentation describes the current state. The record of what changed belongs in the changelog, which this skill does not edit.

## Never Touch

Report these; do not edit them:

- Generated files and build output. Fix the generator instead.
- Test fixtures and golden or snapshot data. Comments inside test files are fair game, but never change assertions or data.
- `CHANGELOG.md` and release-note files.
- `AGENTS.md`, `CLAUDE.md`, and other agent instruction files, and drafts the user marked as protected. Offer to update them instead.
- Vendored or third-party code.

## Decision Rule

When unsure whether a comment or paragraph is slop, ask: would deleting it make a future reader's job harder or the change riskier? If yes, keep it. If you cannot tell, keep it and list it under "Needs your call".

## Workflow

1. Build the target set from Git diff, named paths, or explicit session targets.
2. Read each file well enough to judge comments in context. Do not edit from a diff hunk alone.
3. Apply the removals above. Change comments and prose only; beware of string literals, multiline templates, or regex patterns that resemble comments.
4. Re-read each edited region. Confirm that executable code is completely untouched, for example by checking that `git diff -w` shows changes strictly within comment delimiters or documentation prose blocks.
5. Run the project's existing checks if cheap (typecheck, lint, doc link check). A comment-only edit that breaks a check is a mistake: revert that edit. If there is no runnable check, say so; do not claim verification.

## Examples

### Delete

| Example | Reason |
| --- | --- |
| `// Increment the retry counter` above `retries += 1;` | Restates the code. |
| `// Moved here from the route handler in the March refactor.` | Git owns this history. |
| `/** Gets the user. */` on private `function getUser()` | Repeats identifier without adding contract or context. |
| README section "Phase 2: done, all tests pass" | Finished log, not current guidance. |

### Keep

| Example | Reason |
| --- | --- |
| `// Step 2: Validate handshake token before processing body` | Stage navigation signpost in complex flow. |
| `// Ported from upstream/project-x under Apache 2.0` | Third-party attribution / compliance, not slop. |
| `/** Get user by ID. */` on public exported `export function getUserById(id: string)` | Useful IDE hover/doc tooltip for exported API. |
| `// eslint-disable-next-line no-console` | Tool directive. |
| `// Measured 2026-10-09 on one revision: uploads failed 100% with ERR timeout.` | The date is part of the measurement claim. |
| `// Feature paused while the upstream API is unavailable.` above commented call | Deliberate off-switch; keep and report. |
| `// TODO: improve this` | Vague, but not safe to delete; keep and report. |
| ADR section "Why we did not choose Redis" | Explains current design rationale. |

Shortening example:

```ts
// Before
// We tried polling first, but it was slow, so we switched to websockets
// after discussing with the team, and now we use websockets here.
//
// After: 
// Websockets, not polling: polling added ~2s latency under load.
```

## Output

Keep it short; for a small change, a few lines are enough. Otherwise:

- Files changed, with paths.
- What was removed, grouped by type, with one example each.
- What was deliberately kept and why (directives, diagnostics, vague TODOs).
- Needs your call: protected files, ambiguous items, suspicious code noticed but not touched.

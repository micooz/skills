# Batch Plan Execute Skill

English | [中文](README_zh.md)

An Agent Skill for AI coding agents to batch plan and execute tasks.

## Features

- Parallel implementation plan generation (Subagent)
- Parallel implementation based on plans (Subagent)
- Automatic dependency analysis and task dispatching
- Human-in-the-loop review process
- Adaptive requirement changes
- Archiving of original and revised plan versions

## Prerequisites (Recommended)

- Use a coding agent that supports subagents
- Use an AI model optimized for long-context and complex reasoning tasks.

## Why this Skill?

While "Document-First" and "Plan-First" paradigms are best practices, we often fall into a vicious cycle of high-frequency interruptions:

```
Human: Requirements -> AI: Planning -> Human: Review -> AI: Execute -> Human: Inspect -> Repeat
```

Even though AI writes the code, humans still spend much of their day monitoring the AI, handling handovers, and reviewing every minor step.

The design philosophy of this Agent Skill is:

- **Asynchronous** over Synchronous
- **Parallel** over Serial
- **Less HITL** = Less Friction = More Efficient Token Usage = Lower Costs

Use this skill to minimize interaction frequency with AI, freeing your focus for more critical tasks.

For more design philosophy, see [Short Cycle and Long Cycle](#short-cycle-and-long-cycle).

## How to Use?

### Installation

```shell
npx skills add micooz/batch-plan-execute
```

### Workflow

1. **(Human)** Write a requirement document, e.g., `requirements.md`:

```md
# 2026-04-01 Iteration

## Bugfix

- xxx
- xxx

## Feature 1

- xxx
- xxx

## Feature 2

- xxx
- xxx
```

> **Tips:** Manually modularizing your requirements helps human readability.

> **Tips:** It is recommended to maintain requirements in date-based folders:

```diff
 .docs
 └── 2026-04-02
+    └── requirements.md
```

2. **(AI)** Activate the skill and provide the requirement document:

```shell
$batch-plan-execute path/to/requirements.md
```

Resulting output:

```diff
 .docs
 └── 2026-04-02
+    ├── plans
+    │   ├── chat-history-persistence-api.md
+    │   ├── chat-history-ui.md
+    │   ├── conversation-panel-unification.md
+    │   ├── ui-polish-and-sse-guardrails.md
+    │   └── sqlite-prisma-foundation.md
     └── requirements.md
```

> **Tips:** AI automatically analyzes dependencies and splits tasks into modules.

3. **(Human)** Review the generated plans in the `plans/` directory.

Insert comments using HTML blocks `<!-- xxx -->` anywhere in the plan file (e.g., `plans/some-feature.md`).

> **Tips:** If a revision exists (e.g., `xxx.rev-n.md`), always review the latest version.

4. **(AI)** Revise the plans.

After adding review comments, run the command again:

```shell
$batch-plan-execute path/to/requirements.md
```

AI automatically revises the plans:

```diff
 .docs
 └── 2026-04-02
     ├── plans
     │   ├── chat-history-persistence-api.md
+    │   ├── chat-history-persistence-api.rev-1.md
     │   ├── chat-history-ui.md
     │   ├── conversation-panel-unification.md
     │   ├── ui-polish-and-sse-guardrails.md
+    │   ├── ui-polish-and-sse-guardrails.rev-1.md
     │   └── sqlite-prisma-foundation.md
     └── requirements.md
```

> **Tips:** Files without review comments will not generate new revisions.

5. **(AI)** Execute the plans.

Once all plans are reviewed, enter "Start execution" or use the command in a new session:

```shell
$batch-plan-execute path/to/requirements.md 开始执行
```

> **Tips:** If there are unresolved comments in the latest revision, AI will block execution.

Example:

```
- ui-polish-and-sse-guardrails: using rev-1, executable
- chat-history-persistence-api: using rev-1, executable
- conversation-panel-unification: no comments in latest, executable
- sqlite-prisma-foundation: latest version has comments, BLOCKED
- chat-history-ui: latest version has comments, BLOCKED
```

Please resolve all comments before proceeding with execution.

6. **(Human)** Inspect the results.

Verify the implementation according to your requirements.

## Conventions

### Handling Pending Decisions

AI will use `【⚠ Decision Required ⚠】` markers for items that need your choice:

```md
## Key Changes
- xxx 【⚠ Decision Required ⚠】
a. (Recommended) xxx
b. xxx
c. xxx
```

Refer to the "Plan Review" section below to handle these.

### Plan Review

Use HTML comment blocks `<!--  -->` for feedback.

> **Tips:** VS Code shortcut: `Command + /` (macOS) or `Ctrl + /` (Windows).

```md
# Feature Name
<!-- Change this to: xxx -->

- xxx 【⚠ Decision Required ⚠】
a. (Recommended) xxx
b. xxx
c. xxx
<!-- Option a. -->
```

### Requirement Changes

1. **Deprecate items:** Delete them directly or comment them out with `<!-- -->`.
2. **Add items:** Simply add new lines.
3. **Modify items:** Edit existing text.

> **Tips:** After updating the requirement document, run `$batch-plan-execute requirements.md` to update the plans.

## Other Tips

- In VS Code-like IDEs, use the `@command:workbench.files.action.compareFileWith` command to compare differences between revisions.
- Switch to "Reasoning" or "Deep Thinking" models during the planning phase to improve document quality.

## Short Cycle and Long Cycle

Traditional agent coding workflows can be described as a **Short Cycle**, where the human and agent operate in a single-threaded loop.

Single-threading leads to more interaction rounds, fragmented attention, and higher Token consumption:

```
+------------------------+       +------------------+       +----------------+
| User: Requirement Item | ----> | Agent: Planning  | ----> | User: Review   |
+------------------------+       +------------------+       +----------------+
                                                                    |
                                                                    v
                                   +---------------+       +----------------+
                        Loop <---- | User: Inspect | <---- | Agent: Execute |
                                   +---------------+       +----------------+
```

We aim to shift this workflow to a **Long Cycle** using multi-threaded asynchronous collaboration.

Multi-threading means fewer interaction rounds, better focus, and more effective use of Tokens:

```
                 +------------------------+
                 | User: Requirement List |
                 +------------------------+
                   /          |          \
                  v           v           v
+------------------+ +------------------+ +------------------+
| SubAgent:        | | SubAgent:        | | SubAgent:        |
| Planning A       | | Planning B       | | Planning C       |
+------------------+ +------------------+ +------------------+
                 \           |             /
                   v         v           v
                     +----------------+
                     |  User: Review  |
                     +----------------+
                      /       |       \
                     v        v        v
+------------------+ +------------------+ +------------------+
| SubAgent:        | | SubAgent:        | | SubAgent:        |
| Execute A        | | Execute B        | | Execute C        |
+------------------+ +------------------+ +------------------+
                  \           |             /
                    v         v            v
                     +------------------+
                     |  User: Inspect   |
                     +------------------+
                              |
                              v
                            Loop
```

## License

MIT

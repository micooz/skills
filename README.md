# Batch Plan Execute Skill

English | [中文](README_zh.md)

An Agent Skill for coding agents to write and execute plans in batches.

## Features

- Write planning documents in parallel from requirements (Subagents)
- Execute in parallel from the plans (Subagents)
- Automatically analyze dependencies in requirements and dispatch tasks
- Free-form human review
- Adaptive to requirement changes
- Save original and revised versions to disk for archival

## Prerequisites (Recommended)

- Use a coding agent that supports Subagents.
- Use an AI model that is good at handling long-running tasks.

## Why Is This Skill Needed?

Document-first and plan-first programming are good practices. But we seem to have entered a vicious cycle of frequent interruptions:

```
Human writes requirements -> AI planning -> Human review -> AI execution -> Human acceptance -> Repeat
```

Humans no longer need to write code themselves. But we still sit in front of the computer all day watching AI work. We frequently handle AI handoffs and review the plans and results it produces.

The design philosophy of this Agent Skill is:

- Asynchronous over synchronous
- Parallel over serial
- Less HITL = less friction = higher token efficiency = lower cost

Use this Skill to reduce interaction with AI. Save your energy for more important things.

For more design ideas, see: [Short Cycle and Long Cycle](#short-cycle-and-long-cycle)

## How to Use

### Installation

```shell
npx skills add micooz/batch-plan-execute
```

### Workflow

1. (Human) Write a requirements document, for example `requirements.md`:

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

> Tips: Splitting modules manually makes things easier for humans to read.

> Tips: It is recommended to keep each day's requirements in a date-based folder:

```diff
 .docs
 └── 2026-04-02
+    └── requirements.md
```

2. (AI) Activate the skill and provide the requirements document:

```shell
$batch-plan-execute path/to/requirements.md
```

After execution, it produces:

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

> Tips: AI will analyze feature dependencies in the requirements and split them into modules automatically.

3. (Human) Review the generated planning documents under `plans/`

Insert comment blocks such as `<!-- xxx -->` anywhere in a planning document, such as `plans/some-feature.md`.

> Tips: If an AI revision already exists (`xxx.rev-n.md`), review the latest one.

4. (AI) Revise the plans

After writing your review comments, run it again:

```shell
$batch-plan-execute path/to/requirements.md
```

After AI revises them, it produces:

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

> Tips: Documents without review comments will not generate revision versions.

5. (AI) Execute the plans

After all plans have been reviewed, enter `implement now`, or enter this in a new session:

```shell
$batch-plan-execute path/to/requirements.md implement now
```

> Tips: If the latest revision still has unresolved review comments, AI will refuse to execute.

For example:

```
- ui-polish-and-sse-guardrails: using rev-1, executable
- chat-history-persistence-api: using rev-1, executable
- conversation-panel-unification: no comments in latest, executable
- sqlite-prisma-foundation: latest version has comments, BLOCKED
- chat-history-ui: latest version has comments, BLOCKED
```

At this point, go back to the previous step. Let AI finish the review comments before executing again.

6. (Human) Accept the results

Verify the results based on your own requirements.

## Conventions

### Handling Pending Items

AI will leave a `【⚠ Decision Required ⚠】` marker in the planning document when it needs you to choose an option:

```md
## Key Changes
- xxx【⚠ Decision Required ⚠】
a. (Recommended) xxx
b. xxx
c. xxx
```

See `Plan Review` below for how to handle pending items.

### Plan Review

Insert HTML comment blocks `<!--  -->` for review.

> Tips: Shortcut on macOS: `Command + /`, shortcut on Windows: `Ctrl + /`.

```md
# Some Feature
<!-- Change to: xxx -->

- xxx【⚠ Decision Required ⚠】
a. (Recommended) xxx
b. xxx
c. xxx
<!-- Use a. -->
```

### Requirement Changes

1. Deprecated requirement items: delete them directly, or comment them out with `<!-- -->`.
2. New requirement items: add them directly.
3. Modified requirement items: edit them directly.

> Tips: After the requirements document changes, run `$batch-plan-execute requirements.md` to update the plans.

## Other Tips

- In VS Code-like IDEs, use `@command:workbench.files.action.compareFileWith` to compare revision versions.
- Switch to a deep-thinking model in the planning phase to improve plan quality.

## Short Cycle and Long Cycle

I call past Agent Coding workflows the Short Cycle. In the Short Cycle, humans and agents work in a single-threaded mode.

Single-threading often leads to more rounds of interaction, less focus, and more token use:

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

We need to change this workflow. We need a multi-threaded and asynchronous collaboration model. This extends the Short Cycle into a Long Cycle.

Multi-threading means fewer rounds of interaction, better focus, and better token use.

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

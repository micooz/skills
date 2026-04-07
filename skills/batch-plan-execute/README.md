# Batch Plan Execute Skill

English | [中文](README_zh.md)

An Agent Skill for coding agents to write plans and execute them in batches.

## Features

- Write plan documents in parallel from tasks using Subagents
- Execute plans in parallel using Subagents
- Automatically analyze dependencies in tasks and assign execution work
- Support free-form human review
- Adapt to task changes
- Save original and revised versions to disk for archival
- Provide `checklist.md` to support acceptance review

## Prerequisites (Recommended)

- Use a coding agent that supports Subagents.
- Use an AI model that is good at long-horizon tasks.

## Why Is This Skill Needed?

Document-first and plan-first programming are good practices, but we seem to have entered a vicious cycle of frequent interruptions:

```text
Human provides tasks -> AI planning -> Human review -> AI execution -> Human acceptance -> Repeat
```

We no longer need humans to write code all day, but we still sit in front of the computer watching AI work, handling frequent AI handoffs, and reviewing the plans and outcomes it produces.

The design philosophy of this Agent Skill is:

- Asynchronous over synchronous
- Parallel over serial
- Less HITL = less friction = higher token efficiency = lower cost

Use this Skill to reduce interaction with AI and free up more energy for more important things.

For more design ideas, see [Short Cycle and Long Cycle](#short-cycle-and-long-cycle).

## How to Use

### Installation / Update

```shell
npx skills add micooz/skills --skill batch-plan-execute
```

### Workflow

1. (Human) Write a task document, for example `tasks.md`:

```md
# Task List

## Module 1

- bug: xxx
- ux: xxx
- feat: xxx

## Module 2

- bug: xxx
- ux: xxx
- feat: xxx
```

> Tips: It is recommended to split the document by feature module. This makes it easier for humans to read and helps reduce agent task conflicts to some extent.

> Tips: It is recommended to keep each day's task iteration in a folder named `{date}`:

```diff
 .docs
 └── 2026-04-02
+    └── tasks.md
```

2. (AI) Activate the skill and provide the task document:

Agent Skills can be activated proactively or passively. Considering environment differences, proactive activation is recommended.

> Note: Different coding agents activate skills differently. The examples below use `OpenCode` syntax:

```shell
# Codex
$batch-plan-execute path/to/tasks.md
# Claude Code / OpenCode
/batch-plan-execute path/to/tasks.md
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
+    ├── checklist.md
     └── tasks.md
```

> Tips: AI will automatically analyze dependencies in the tasks and split the work into modules.
> Tips: `checklist.md` consolidates the original tasks and the latest review decisions into the final acceptance / verification checklist.

3. (Human) Review the planning documents generated under `plans/`

Insert a comment like `<!-- xxx -->` anywhere in a plan document to leave review feedback.

```md
- Some feature
<!-- Change to: xxx -->
```

AI will leave a `【⚠ Decision Required ⚠】` marker in the planning document when it needs you to choose an option. Use `<!-- xxx -->` in the same way to select one:

```md
## Key Changes
- xxx【⚠ Decision Required ⚠】
a. (Recommended) xxx
b. xxx
c. xxx
<!-- Use a. -->
```

> Tips: Comment shortcut: macOS `Command + /`, Windows `Ctrl + /`.
> Tips: If a revision already exists (`xxx.rev-n.md`), review the latest revision instead.

4. (AI) Revise the plans

After writing your review comments, run it again:

```shell
/batch-plan-execute path/to/tasks.md
```

AI will automatically revise the plans and produce:

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
     ├── checklist.md
     └── tasks.md
```

> Tips: Documents without review comments will not generate revision versions.

5. (AI) Execute the plans

After all plans have been reviewed, type `implement now`, or use this in a new session:

```shell
/batch-plan-execute path/to/tasks.md implement now
```

> Tips: If the latest revision still has unresolved review comments, AI will refuse to execute.

For example:

```text
- ui-polish-and-sse-guardrails uses rev-1, executable
- chat-history-persistence-api uses rev-1, executable
- conversation-panel-unification has no comments in the latest draft, executable
- sqlite-prisma-foundation has comments in the latest draft, blocked
- chat-history-ui has comments in the latest draft, blocked
```

At this point, go back to the previous step and let AI finish handling the review comments before executing again.

6. (Human) Accept the results

Use `checklist.md` to verify each change and make sure the agent fully executed the plan.

```md
- [x] bugfix
- [] feature
```

> Tips: You can ask the agent to use this file to handle any missed task items.

7. (Human) Modify, delete, or add tasks

For modifications or deletions, edit the task document in place:

```diff
 # Task List

 ## Module 1

 - bug: xxx
- - ux: xxx (delete the task directly)
- - feat: xxx
+ <!-- - feat: xxx --> (delete the task by commenting it out)
```

For new tasks, such as issues discovered during acceptance, it is recommended to append `---` and a new section in the original document:

```diff
 # Task List

 ## Module 1

 - bug: xxx
 - ux: xxx (delete the task directly)
 - feat: xxx

+ ---

+ ## New Tasks

+ - bug: xxx
```

> Tips: After the task document changes, run `/batch-plan-execute tasks.md` again to update the plans.

## Other Tips

- In VS Code-like IDEs, use `@command:workbench.files.action.compareFileWith` to compare differences between revision versions.
- Increase the model's reasoning effort during the planning phase to improve the quality of the plan documents.

## Short Cycle and Long Cycle

I call the previous Agent Coding workflow the Short Cycle. In the Short Cycle, humans and agents operate in a single-threaded mode.

Single-threading often leads to more rounds of interaction, less focus, and more token consumption:

```text
+-----------------+       +------------------+       +----------------+
| User: Task Item | ----> | Agent: Planning  | ----> | User: Review   |
+-----------------+       +------------------+       +----------------+
                                                              |
                                                              v
                             +---------------+       +----------------+
                  Loop <---- | User: Inspect | <---- | Agent: Execute |
                             +---------------+       +----------------+
```

We need to change this workflow and adopt a multi-threaded asynchronous collaboration model, extending the Short Cycle into a Long Cycle.

Multi-threading means fewer rounds of interaction, easier concentration on one thing, and better token usage.

```text
                 +------------------------+
                 |    User: Task List     |
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

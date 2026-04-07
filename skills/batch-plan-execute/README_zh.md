# Batch Plan Execute Skill

[English](README.md) | 中文

让 Coding Agent 批量编写计划和执行计划的 Agent Skill。

## 特性

- 根据任务并行编写计划文档（Subagents）
- 根据计划并行执行（Subagents）
- 自动分析任务中的依赖关系、自动分派任务执行
- 人类自由评审
- 自适应任务变更
- 原始/修订版本落盘存档
- 提供 checklist.md 辅助验收

## 前置要求（建议）

- 使用支持 Subagents 的 Coding Agent。
- 使用擅长处理长程任务的 AI 模型。

## 为什么需要这个 Skill？

文档优先、计划优先的编程范式是很好的实践，但我们似乎进入了一种被高频打扰的恶性循环：

```text
人出任务 -> AI Planning -> 人 Review -> AI 执行 -> 人验收 -> 重复
```

虽然现在不用人来写代码，但我们一天到晚依然要坐在电脑前守着 AI 干活，高频处理 AI 交接，审核 AI 给出的方案和成果。

这个 Agent Skill 的设计哲学是：

- 异步优于同步
- 并行优于串行
- 更少的 HITL = 更少的摩擦 = 更高效的 token 利用率 = 节省成本

使用这个 Skill 来减少和 AI 的交互，释放更多精力到更重要的事情上。

更多设计理念参见：[短循环和长循环](#短循环和长循环)

## 如何使用？

### 安装/更新

```shell
npx skills add micooz/skills --skill batch-plan-execute
```

### 工作流

1. (Human) 编写任务文档，比如：`tasks.md`：

```md
# 任务清单

## 模块一

- bug: xxx
- ux: xxx
- feat: xxx

## 模块二

- bug: xxx
- ux: xxx
- feat: xxx
```

> Tips: 建议按功能模块分段：一是方便人类阅读，二是在一定程度上避免 agent 任务冲突。

> Tips: 建议按 `{日期}` 命名文件夹维护每一天的任务迭代：

```diff
 .docs
 └── 2026-04-02
+    └── tasks.md
```

2. (AI) 激活技能并提供任务文档：

Agent Skills 可以以主动或被动的方式激活，考虑到环境差异，推荐主动激活。

> 注意：注意不同 Coding Agent 主动激活 Skill 的方式不同，后续文档中均以 `OpenCode` 写法为例：

```shell
# Codex
$batch-plan-execute path/to/tasks.md
# Claude Code / OpenCode
/batch-plan-execute path/to/tasks.md
```

执行后产出：

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

> Tips: AI 会根据任务自动分析功能依赖关系并拆好模块。
> Tips: `checklist.md` 汇总原始任务与最新评审意见，作为最终的验收/核对清单。

3. (Human) 评审 `plans/` 下生成的计划文档

在计划文档的任意位置插入注释 `<!-- xxx -->` 进行评审。

```md
- 某功能
<!-- 改成：xxx -->
```

AI 会在计划文档中留下 `【⚠ Decision Required ⚠】` 标记需要你确认使用哪种方案，同样使用 `<!-- xxx -->` 进行选择：

```md
## Key Changes
- xxx【⚠ Decision Required ⚠】
a. (Recommended) xxx
b. xxx
c. xxx
<!-- 采用 a. -->
```

> Tips: 插入注释快捷键：macOS `Command + /`，Windows `Ctrl + /`。
> Tips: 如果已经存在修订版本（xxx.rev-n.md），请在最新修订版本中进行评审。

4. (AI) 修订计划

写好评审意见后，再次执行：

```shell
/batch-plan-execute path/to/tasks.md
```

AI 自动修订后产出：

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

> Tips: 没有评审意见的文档不会产生修订版本。

5. (AI) 执行计划

所有计划评审完毕后，输入 `开始执行`，或是在一个新会话中输入：

```shell
/batch-plan-execute path/to/tasks.md 开始执行
```

> Tips: 如果最新修订版本中还有评审意见未解决，AI 会拒绝执行。

比如：

```
- ui-polish-and-sse-guardrails 使用 rev-1，可执行
- chat-history-persistence-api 使用 rev-1，可执行
- conversation-panel-unification 当前最新稿无 comment，可执行
- sqlite-prisma-foundation 当前最新稿有 comment，阻塞
- chat-history-ui 当前最新稿有 comment，阻塞
```

此时请回到上一步让 AI 处理完评审意见后再执行。

6. (Human) 验收结果

对照 `checklist.md` 验收每一个变更结果以确保 agent 完全执行了计划。

```md
- [x] bugfix
- [] feature
```

> Tips: 可要求 agent 参考这份文件处理遗漏的任务点。

7. (Human) 修改、删除、新增任务

对于修改、删除任务，直接在任务文档中原地修改和删除：

```diff
 # 任务清单

 ## 模块一

 - bug: xxx
- - ux: xxx (直接删除任务)
- - feat: xxx
+ <!-- - feat: xxx --> (通过注释删除任务)
```

对于新增任务，比如验收环节发现的问题需要处理，建议在原文档中追加 `---` 和新段落：

```diff
 # 任务清单

 ## 模块一

 - bug: xxx
 - ux: xxx (直接删除任务)
 - feat: xxx

+ ---

+ ## 新增任务

+ - bug: xxx
```

> Tips: 任务文档变更后，重新执行 /batch-plan-execute tasks.md 更新计划。

## 其他技巧提示

- 在 VS Code-like 的 IDE 中通过 `@command:workbench.files.action.compareFileWith` 命令比较不同修订版本之间的差异。
- 在计划阶段提升模型的 reasoning effort 提升计划文档的质量。

## 短循环和长循环

我将过往的 Agent Coding 工作流称之为短循环（Short Cycle），短循环可以看作人和 Agent 处于单线程运行态。

单线程往往导致更多轮次的交互、更少的注意力和更多的 token 消耗：

```
+-----------------+       +------------------+       +----------------+
| User: Task Item | ----> | Agent: Planning  | ----> | User: Review   |
+-----------------+       +------------------+       +----------------+
                                                              |
                                                              v
                             +---------------+       +----------------+
                  Loop <---- | User: Inspect | <---- | Agent: Execute |
                             +---------------+       +----------------+
```

我们需要改变这种工作流程，采用多线程异步协作机制，将短循环拉长为长循环（Long Cycle）。

多线程意味着更少轮次的交互、更容易在一件事情上集中注意力、更利于把 token 用在刀刃上。

```
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

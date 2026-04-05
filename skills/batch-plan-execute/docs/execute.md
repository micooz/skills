# Execute Mode

## Inputs

Resolve execution targets in this order:

1. an explicit plan file path
2. an explicit `plans/` directory
3. the latest plan lineage next to the referenced requirement source

Use the latest reviewed artifact for each selected module lineage.

Fail immediately if the latest artifact still contains unresolved HTML review comments.

## Preflight

Before spawning execution subagents:

- resolve the latest reviewed artifact for each selected module lineage
- confirm each selected module plan declares its dependency layer
- confirm each selected module plan declares the upstream modules that must already be complete
- confirm shared-change ownership boundaries are explicit in the selected plans
- confirm each selected module plan declares the file or subsystem write scope it owns

Treat approved plans as the execution boundary source of truth. Do not re-scope modules, re-derive write ownership, or re-plan dependency layering during execute mode.

## Worker Dispatch

Spawn implementation-oriented subagents for execution work.

Each execution subagent must receive:

- the exact module plan body
- the dependency layer for that module
- the upstream modules that must already be complete
- the shared-change ownership boundaries
- the file or subsystem write scope it owns
- the instruction that it is not alone in the codebase and must not revert unrelated edits
- the instruction to implement, validate locally when possible, and report changed files

Use these rules:

- Dispatch execution subagents in the dependency-layer order declared by the selected plans.
- Within a ready layer, parallelize only modules whose plan-defined ownership boundaries do not overlap on the same schema, interface, migration, utility, or infrastructure change.
- If a shared change is needed by multiple modules, give it one owner execution subagent and make other execution subagents depend on that result.
- If an execution subagent uncovers that its plan is no longer valid against the repository, stop the affected branch and escalate to the main agent instead of freelancing a new plan.

## Main-Agent Responsibilities

The main agent owns:

- execution-subagent selection and dispatch order
- shared-change ownership decisions
- integration of execution-subagent results
- conflict resolution
- final verification

Use these rules:

- Review execution-subagent outputs before advancing downstream layers.
- Do not let downstream work continue if an upstream layer failed validation.
- Dispatch directly from approved plan boundaries instead of re-grounding the repository to redefine scope.
- Preserve user changes and unrelated repo edits.
- Let exceptions and test failures surface. Do not add fallback logic unless the plan explicitly requires it.

## Verification

Run validation in this order:

1. the narrowest module-specific checks that prove the implemented change works
2. broader checks for the touched area
3. final integrated repo checks when the change surface warrants it

Prefer the repository's existing test, lint, typecheck, build, or other validation commands as appropriate for the touched scope.

If only a subset of checks is relevant, run that narrower scope first and still report what broader validation remains unrun.

## Completion Criteria

Execution is complete only when:

- every selected module in the ready scope is implemented
- required validations for those modules pass
- downstream dependencies, if any, have either completed or been explicitly deferred by plan
- the final report names the changed areas, validations run, and any remaining blockers

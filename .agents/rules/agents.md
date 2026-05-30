---
alwaysApply: true
---

# Agent Rules

Agent root: ./.agents/

## Project references

When starting a task, you must read the following files

1. Project philosophy: ./PHILOSOPHY.md
2. Project principles: ./PRINCIPLES.md
3. agent delegation patterns: ./agent-delegation.md
4. slim agent architecture: ./slim-agent-architecture.md
5. Project-specific customizations: ./.custom/README.md

# Custom agents

This project has 11 specialized agent roles with 31 activity-based specializations. Each agent brings deep expertise in a specific domain, enabling Claude Code to tackle complex tasks with specialist knowledge.

1. Reference: ./agent-roles.md
2. Agents folder: ./agents/
3. Agent delegation patterns: ./agent-delegation.md
4. Slim agent architecture: ./slim-agent-architecture.md

## Skills, Agents and Commands Index

**Purpose**: Use this index to find the proper skill, agent or command to use when you are working
**when**: When you are working on a task and your context specifies a command, skill, agent or integration point.

## Tools available

Map from tool names used in commands, skills, and agents to the Cursor/agent tool that fulfills them.

| Referenced in commands / skills / agents | Cursor/agent tool | Notes |
|----------------------------------------|--------------------|-------|
| **Task** | `mcp_task` | Delegate to specialist agents; use `subagent_type` to choose agent. "Delegate via Task tool" means use `mcp_task`. |
| **TaskOutput** | (result of `mcp_task`) | Not a separate tool; the agent’s reply is the task output. |
| **TodoWrite** | `TodoWrite` | Track phases or task lists (pending, in_progress, completed, cancelled). |
| **Bash** | `Shell` | Run shell commands (bash, git, npm, etc.). |
| **LS** | `Shell` or `Glob` | Listing dirs: run `Shell` with `ls` or use `Glob` for file discovery. |
| **Grep** | `Grep` | Ripgrep search in the codebase. |
| **Glob** | `Glob` | Find files by glob pattern. |
| **Read** | `Read` | Read file (or image) contents. |
| **Write** | `Write` | Create or overwrite a file. |
| **Edit** | `StrReplace` | In-file edits via exact string replacement. |
| **MultiEdit** | `StrReplace` | Multiple edits: use several `StrReplace` calls or `replace_all` where appropriate. |
| **AskUserQuestion** | *(no tool)* | Ask the user in the chat message; no dedicated tool. |
| **Skill** | *(no tool)* | Use `Read` on the skill’s SKILL.md and follow its instructions; no dedicated tool. |
| **WebSearch** | `WebSearch` | Web search for up-to-date information. |
| **WebFetch** | `mcp_web_fetch` | Fetch URL content as markdown. |

For every Tool that is not listed, infeer the proper tool in the table above

## Task Workflow

Before starting work, assess the task complexity to determine how much context to gather. The goal is **just-in-time context**: gather only what the current task demands.

### Navigation Rule: Grep to Find, LSP to Understand

Use **Grep/Glob** for discovery (locating files, concept search, string patterns, config files).
Use **LSP** for comprehension once you've found the area (call hierarchy, find references, type resolution, protocol implementations).

| Need | Tool | Example |
|------|------|---------|
| Locate code by concept or pattern | Grep/Glob | "Where is the payment logic?" |
| String/config/non-code search | Grep/Read | "What's in .env?", "Find all TODOs" |
| Impact analysis | LSP | "What breaks if I change this signature?" |
| Call hierarchy | LSP | "How does data flow from API to DB?" |
| Protocol/interface conformance | LSP | "What types implement AuthProvider?" |
| Type resolution | LSP | "What does this function return?" |

LSP requires prerequisites (Swift: project built; TS: node_modules installed + tsconfig.json). If prerequisites aren't met, fall back to Grep.

### Scenario Assessment

| Signal | Likely Scenario |
|--------|----------------|
| Single file mentioned, small change described | **Quick Task** |
| `/start:specify` or `/start:implement` invoked | **Spec-Driven Feature** |
| Multiple files/modules affected, no spec | **Multi-File Work** |
| PR review, code review, `/start:review` | **Code Review** |
| Bug report, error investigation, `/start:debug` | **Debugging** |

### Quick Task

**When**: Bug fix, single-file refactor, code improvement, answering a question about specific code.

**Do**:
- Read the target file(s)
- Make the change

**Skip**: Memory queries, LSP initialization, pattern detection, tech-stack detection.

**Recommended skills**: None upfront. Load only if the task reveals unexpected complexity.

### Spec-Driven Feature

**When**: `/start:specify`, `/start:implement`, or user describes a feature that needs planning.

**Do** (in order):
1. `make -f betteragents.mk vague q="[feature domain]"` — shallow scan for prior knowledge
2. If vague returns hits → `make -f betteragents.mk remember q="[topic]"` for recalled knowledge
3. If deeper context needed → `make -f betteragents.mk retrieve q="[specific area]"` or `ask q="[refined question]"` for codebase context
4. Proceed with the command workflow (the command itself loads its required skills)

**Navigation**: Grep/Glob to explore the domain area. During implementation phase, load LSP for impact analysis and safe refactoring across files.

**Skip**: Tech-stack detection (unless first session on project).

**Recommended skills**: `Skill(agent-memory)` (context gathering), `Skill(tech-stack-detection)` (first time only), `Skill(lsp-swift)` or `Skill(lsp-typescript)` (implementation phase — for call hierarchy and reference tracing).

**After completion**: `journal` the outcome.

### Multi-File Work

**When**: Task spans multiple files/modules without a formal spec. Examples: refactoring across modules, adding cross-cutting concerns, migrations.

**Do** (in order):
1. `make -f betteragents.mk vague q="[topic]"` — check for prior knowledge
2. If hits → `make -f betteragents.mk remember q="[topic]"` for recalled knowledge
3. If deeper context needed → `make -f betteragents.mk retrieve q="[specific area]"` for codebase context
4. Grep/Glob to locate all affected files
5. LSP to understand relationships between them (call hierarchy, find references, type flow)
6. `Skill(pattern-detection)` — understand conventions before writing
7. Proceed with implementation

**Skip**: Full spec workflow (unnecessary overhead for ad-hoc work).

**Recommended skills**: `Skill(agent-memory)`, `Skill(pattern-detection)`, `Skill(codebase-navigation)` (if architecture is unclear), `Skill(lsp-swift)` or `Skill(lsp-typescript)` (for impact analysis and safe propagation of changes).

**After completion**: `learn` any discovered patterns/gotchas, `journal` the outcome.

### Code Review

**When**: Reviewing PRs, branches, staged changes, or specific files.

**Do**:
1. Read the diff and full file context
2. `Skill(pattern-detection)` — verify convention alignment
3. If change touches public APIs or shared interfaces → LSP to verify blast radius (find references, call hierarchy)

**Skip**: Memory queries (unless reviewing a domain you've never seen), tech-stack detection.

**Recommended skills**: `Skill(code-review)` (orchestrates multi-lens review), `Skill(pattern-detection)`, `Skill(lsp-swift)` or `Skill(lsp-typescript)` (only for blast radius verification on interface/API changes).

### Debugging

**When**: Bug report, error investigation, root-cause analysis.

**Do**:
1. `make -f betteragents.mk vague q="[error/symptom]"` — has this been seen before?
2. If hits → `make -f betteragents.mk remember q="[error/symptom]"` for recalled knowledge
3. Read error context (logs, stack traces, reproduction steps)
3. Grep to locate the error origin
4. LSP to trace the call hierarchy from the error site upward — understand how the bug propagates

**Skip**: Pattern detection, tech-stack detection.

**Recommended skills**: `Skill(bug-diagnosis)`, `Skill(lsp-swift)` or `Skill(lsp-typescript)` (call hierarchy tracing from error site), `Skill(agent-memory)`.

**After resolution**: `learn` the root cause if it reveals a reusable insight.

### Escalation

If a Quick Task reveals unexpected complexity (touches many files, requires architectural understanding), **ask the user** before escalating. Present what you found and suggest upgrading to Multi-File Work or Spec-Driven Feature workflow.

### Skill calls

Some commands can target to a specific skill. For example, the command `Skill(git-workflow)` will target the `git-workflow` skill in the folder ./.agents/skills/git-workflow/SKILL.md.

You will see that the skills are marked with `Skill(skill-name)` in the commands. When you see this link, you shall:

1. USE that skill
2. Notify the user that you are using the skill: `Using skill: Skill(skill-name)`

### Command Triggers (`/start:*`)

- **`/start:brainstorm` → Command**: `./.agents/commands/brainstorm.md`
  - **Purpose**: Brainstorm ideas into designs with optional UX specifications through collaborative dialogue.
  - **Primary skills**:
    - `Skill(brainstorming)` (idea exploration, approach evaluation, design presentation)
    - `Skill(ux-dls)` (optional UX design after design approval)
  - **Output**: `docs/ideas/<name>/design.md` + optional `docs/ideas/<name>/ux/*.dls`

- **`/start:constitution` → Command**: `./.agents/commands/constitution.md`
  - **Purpose**: Create or update the project constitution via discovery.
  - **Primary skills**: `Skill(constitution-validation)`
  - **Related integrations** (from skills): calls `Skill(constitution-validation)`, which is also invoked by `/start:validate`, `/start:implement`, `/start:review`, `/start:specify`.

- **`/start:validate` → Command**: `./.agents/commands/validate.md`
  - **Purpose**: Validate specifications, implementations, or understanding.
  - **Primary skills**: `Skill(specification-validation)`
  - **Related integrations** (from skills): `Skill(drift-detection)` (Mode C), `Skill(constitution-validation)` (Mode E) when validating against constitution or comparing spec vs implementation.

- **`/start:specify` → Command**: `./.agents/commands/specify.md`
  - **Purpose**: Create/manage specifications (PRD, DLS, SDD, PLAN) from a brief description.
  - **Primary skills**:
    - `Skill(specification-management)` (spec directory + workflow)
    - `Skill(requirements-analysis)` (PRD)
    - `Skill(ux-dls)` (UX design — optional, after PRD)
    - `Skill(architecture-design)` (SDD)
    - `Skill(implementation-planning)` (PLAN)
  - **Additional skills**:
    - `Skill(constitution-validation)` (planning/SDD alignment, if `CONSTITUTION.md` exists)
    - `Skill(git-workflow)` (optional git/PR workflow)

- **`/start:implement` → Command**: `./.agents/commands/implement.md`
  - **Purpose**: Execute implementation plan phase-by-phase.
  - **Primary skills**:
    - `Skill(specification-management)` (read PLAN)
    - `Skill(drift-detection)` (phase checkpoints)
    - `Skill(constitution-validation)` (constitution enforcement, if present)
    - `Skill(implementation-verification)` (final validation)
  - **Additional skills**: `Skill(git-workflow)` for optional branch/commit/PR management.

- **`/start:review` → Command**: `./.agents/commands/review.md`
  - **Purpose**: Multi-agent code review with specialized perspectives.
  - **Primary agents**: Uses the review-focused Task subagents (see Agents index below).
  - **Constitution integration**: Includes constitution perspective when `CONSTITUTION.md` exists, which uses `Skill(constitution-validation)` for compliance.

- **`/start:analyze` → Command**: `./.agents/commands/analyze.md`
  - **Purpose**: Discover and document business rules, technical patterns, and system interfaces.
  - **Primary skills**: `Skill(codebase-analysis)`

- **`/start:refactor` → Command**: `./.agents/commands/refactor.md`
  - **Purpose**: Safe refactoring focused on maintainability without behavior change.
  - **Primary skills**: `Skill(safe-refactoring)`

- **`/start:debug` → Command**: `./.agents/commands/debug.md`
  - **Purpose**: Systematic conversational debugging and root-cause analysis.
  - **Primary skills**: `Skill(bug-diagnosis)`

- **`/start:simplify` → Command**: `./.agents/commands/simplify.md`
  - **Purpose**: Code simplification and cleanup while preserving behavior.
  - **Primary skills**: `Skill(safe-refactoring)`

- **`/start:document` → Command**: `./.agents/commands/document.md`
  - **Purpose**: Generate and maintain project documentation (code, API, README, audit).
  - **Primary skills**: `Skill(technical-writing)`

- **`/start:design-product` → Command**: `./.agents/commands/design-product.md`
  - **Purpose**: Define product MVP with features, stakeholders, subscription plans, and prioritized roadmap through collaborative discovery.
  - **Primary skills**:
    - `Skill(brainstorming)` (discovery, idea exploration)
    - `Skill(user-research)` (personas, journeys)
    - `Skill(requirements-elicitation)` (requirements, use cases, flows)
    - `Skill(mvp-architect)` (MVP scoping)
    - `Skill(product-strategy)` (business model, positioning)
    - `Skill(product-management)` (roadmap)
    - `Skill(feature-prioritization)` (prioritization)
    - `Skill(ux-dls)` (optional DLS for screens/flows)
  - **Output**: `docs/project/product-vision.md`, `mvp-scope.md`, `business-model.md`, `product-roadmap.md`, `use-cases/*.md`, optional `dls/*.dls`, `resources.md`

- **`/start:memory` → Command**: `./.agents/commands/memory.md`
  - **Purpose**: Interact with agent memory — teach knowledge or recall what agents know.
  - **Primary skills**: `Skill(agent-memory)`

### Skill Invocations (`Skill(name)`)

- **`Skill(constitution-validation)` → Skill**: `./.agents/skills/constitution-validation/SKILL.md`
  - **Called by commands**: `/start:constitution`, `/start:implement`, `/start:review`, `/start:specify`, and by `/start:validate` when validating constitutions.
  - **Integration points (from skill)**: `/start:constitution`, `/start:validate` (Mode E), `/start:implement`, `/start:review`, `/start:specify`.

- **`Skill(drift-detection)` → Skill**: `./.agents/skills/drift-detection/SKILL.md`
  - **Called by commands**: `/start:implement` (phase drift checks), `/start:validate` (Mode C comparison validation).
  - **Integration points (from skill)**: `/start:implement`, `/start:validate` (Mode C).

- **`Skill(specification-validation)` → Skill**: `./.agents/skills/specification-validation/SKILL.md`
  - **Called by commands**: `/start:validate` (core validation methodology).

- **`Skill(specification-management)` → Skill**: `./.agents/skills/specification-management/SKILL.md`
  - **Called by commands**: `/start:specify` (spec lifecycle), `/start:implement` (PLAN reading and phase loading).

- **`Skill(requirements-analysis)` → Skill**: `./.agents/skills/requirements-analysis/SKILL.md`
  - **Called by commands**: `/start:specify` (PRD phase).

- **`Skill(architecture-design)` → Skill**: `./.agents/skills/architecture-design/SKILL.md`
  - **Called by commands**: `/start:specify` (SDD phase).

- **`Skill(implementation-planning)` → Skill**: `./.agents/skills/implementation-planning/SKILL.md`
  - **Called by commands**: `/start:specify` (PLAN phase).

- **`Skill(implementation-verification)` → Skill**: `./.agents/skills/implementation-verification/SKILL.md`
  - **Called by commands**: `/start:implement` (completion checks).

- **`Skill(codebase-analysis)` → Skill**: `./.agents/skills/codebase-analysis/SKILL.md`
  - **Called by commands**: `/start:analyze` (scope initialization).

- **`Skill(safe-refactoring)` → Skill**: `./.agents/skills/safe-refactoring/SKILL.md`
  - **Called by commands**: `/start:refactor`, `/start:simplify` (baseline and methodology).

- **`Skill(brainstorming)` → Skill**: `./.agents/skills/brainstorming/SKILL.md`
  - **Purpose**: Collaborative dialogue to turn ideas into fully formed designs through context exploration, clarifying questions, approach evaluation, and incremental design presentation.
  - **Called by commands**: `/start:brainstorm` (all phases of idea exploration and design).

- **`Skill(bug-diagnosis)` → Skill**: `./.agents/skills/bug-diagnosis/SKILL.md`
  - **Called by commands**: `/start:debug` (all phases of debugging).

- **`Skill(technical-writing)` → Skill**: `./.agents/skills/technical-writing/SKILL.md`
  - **Called by commands**: `/start:document` (documentation methodology).

- **`Skill(git-workflow)` → Skill**: `./.agents/skills/git-workflow/SKILL.md`
  - **Called by commands**: `/start:specify`, `/start:implement` (optional git/PR flows).

- **`Skill(agent-coordination)` → Skill**: `./.agents/skills/agent-coordination/SKILL.md`
  - **Purpose**: Execute implementation plans phase-by-phase with checkpoint validation, managing phase transitions, parallel/sequential task delegation, and progress tracking.
  - **Called by commands**: Standalone skill (invoked by orchestrating commands when executing from a PLAN.md).

- **`Skill(agent-debug)` → Skill**: `./.agents/skills/agent-debug/SKILL.md`
  - **Purpose**: Simulate and narrate agent behavior during explicit DEBUG mode sessions without executing state-changing operations, for testing tool usage and orchestration logic.
  - **Called by commands**: Standalone skill (activated only when the user explicitly declares DEBUG mode).

- **`Skill(api-contract-design)` → Skill**: `./.agents/skills/api-contract-design/SKILL.md`
  - **Purpose**: Design REST and GraphQL APIs with contract-first methodology, resource modeling, HTTP status code semantics, pagination, versioning, and OpenAPI specification patterns.
  - **Called by commands**: Standalone skill.

- **`Skill(architecture-selection)` → Skill**: `./.agents/skills/architecture-selection/SKILL.md`
  - **Purpose**: Select and document system architecture patterns (monolith, microservices, event-driven, serverless) using C4 modeling, scalability strategies, and ADR templates.
  - **Called by commands**: Standalone skill.

- **`Skill(code-quality-review)` → Skill**: `./.agents/skills/code-quality-review/SKILL.md`
  - **Purpose**: Evaluate code across six dimensions (correctness, design, readability, security, performance, testability) with anti-pattern catalog and prioritized severity tiers.
  - **Called by commands**: Standalone skill.

- **`Skill(code-review)` → Skill**: `./.agents/skills/code-review/SKILL.md`
  - **Purpose**: Coordinate multi-agent code reviews across four specialized lenses (security, performance, quality, testing) with confidence scoring and severity classification.
  - **Called by commands**: Standalone skill (triggered when reviewing PRs, branches, staged changes, or specific files).

- **`Skill(codebase-navigation)` → Skill**: `./.agents/skills/codebase-navigation/SKILL.md`
  - **Purpose**: Navigate and understand project structures efficiently using systematic Glob/Grep patterns, architecture mapping, and dependency tracing.
  - **Called by commands**: Standalone skill.

- **`Skill(coding-conventions)` → Skill**: `./.agents/skills/coding-conventions/SKILL.md`
  - **Purpose**: Apply consistent security (OWASP), performance, and accessibility (WCAG 2.1 AA) standards cross-cuttingly with error handling patterns and structured logging guidance.
  - **Called by commands**: Standalone skill (cross-cutting; used by all agents during code review or implementation).

- **`Skill(data-modeling)` → Skill**: `./.agents/skills/data-modeling/SKILL.md`
  - **Purpose**: Design database schemas via ER modeling, normalization through BCNF, intentional denormalization, and Expand-Contract schema evolution strategies.
  - **Called by commands**: Standalone skill.

- **`Skill(deployment-pipeline-design)` → Skill**: `./.agents/skills/deployment-pipeline-design/SKILL.md`
  - **Purpose**: Design CI/CD pipelines with stage sequencing, blue-green/canary/rolling deployment strategies, quality gates, rollback mechanisms, and GitHub Actions patterns.
  - **Called by commands**: Standalone skill.

- **`Skill(documentation-extraction)` → Skill**: `./.agents/skills/documentation-extraction/SKILL.md`
  - **Purpose**: Extract actionable information from READMEs, API docs, technical specs, and configuration files; identify outdated, conflicting, or missing documentation.
  - **Called by commands**: Standalone skill.

- **`Skill(domain-driven-design)` → Skill**: `./.agents/skills/domain-driven-design/SKILL.md`
  - **Purpose**: Apply DDD tactical patterns (entities, value objects, aggregates, domain events, repositories) and strategic patterns (bounded contexts, context mapping, ubiquitous language).
  - **Called by commands**: Standalone skill.

- **`Skill(feature-prioritization)` → Skill**: `./.agents/skills/feature-prioritization/SKILL.md`
  - **Purpose**: Apply RICE, MoSCoW, Kano, value-effort, and Cost of Delay prioritization frameworks with scoring methodologies and decision documentation.
  - **Called by commands**: Standalone skill.

- **`Skill(knowledge-capture)` → Skill**: `./.agents/skills/knowledge-capture/SKILL.md`
  - **Purpose**: Document discovered business rules, technical patterns, and external service interfaces into `docs/domain/`, `docs/patterns/`, and `docs/interfaces/` with deduplication-first workflow.
  - **Called by commands**: Standalone skill (invoked after analysis or implementation when reusable knowledge is found).

- **`Skill(lsp-swift)` → Skill**: `./.agents/skills/lsp-swift/SKILL.md`
  - **Purpose**: Use the Swift LSP (SourceKit-LSP) for code intelligence — go-to-definition, find references, hover, symbol search, call hierarchy, and protocol implementation navigation in Swift projects.
  - **Called by commands**: Standalone skill (use when navigating Swift codebases, understanding types, tracing call hierarchies, or debugging type resolution issues).

- **`Skill(lsp-typescript)` → Skill**: `./.agents/skills/lsp-typescript/SKILL.md`
  - **Purpose**: Use the TypeScript LSP (tsserver) for code intelligence — go-to-definition, find references, hover, symbol search, call hierarchy, and interface implementation navigation in TypeScript/JavaScript projects.
  - **Called by commands**: Standalone skill (use when navigating TS/JS codebases, understanding types, tracing call hierarchies, or debugging import/type resolution issues).

- **`Skill(agent-memory)` → Skill**: `./.agents/skills/agent-memory/SKILL.md`
  - **Purpose**: Use RAG pipeline endpoints (ask, retrieve, learn, remember, journal) to give agents codebase context, persistent memory, and work history. Auto-triggers: learn after discoveries, retrieve during implementation, journal after completing work.
  - **Called by commands**: `/start:memory`. Also standalone — any agent can invoke during implementation or analysis.

- **`Skill(observability-design)` → Skill**: `./.agents/skills/observability-design/SKILL.md`
  - **Purpose**: Design monitoring infrastructure covering metrics, logs, traces, SLI/SLO/error budget frameworks, multi-window alerting, and incident response procedures.
  - **Called by commands**: Standalone skill.

- **`Skill(pattern-detection)` → Skill**: `./.agents/skills/pattern-detection/SKILL.md`
  - **Purpose**: Identify existing codebase naming conventions, architectural patterns, testing patterns, and import/export conventions to ensure new code maintains consistency.
  - **Called by commands**: Standalone skill (used before writing new code or during code review).

- **`Skill(performance-analysis)` → Skill**: `./.agents/skills/performance-analysis/SKILL.md`
  - **Purpose**: Establish performance baselines, profile at CPU/memory/I/O levels using USE and RED methods, identify bottlenecks, and plan capacity using load/stress/soak testing.
  - **Called by commands**: Standalone skill.

- **`Skill(requirements-elicitation)` → Skill**: `./.agents/skills/requirements-elicitation/SKILL.md`
  - **Purpose**: Transform vague ideas into clear, testable specifications using the 5 Whys, stakeholder interviews, user stories, and Given-When-Then acceptance criteria.
  - **Called by commands**: Standalone skill.

- **`Skill(security-assessment)` → Skill**: `./.agents/skills/security-assessment/SKILL.md`
  - **Purpose**: Perform systematic security evaluation using STRIDE threat modeling and OWASP Top 10 review patterns covering injection, broken access control, and cryptographic failures.
  - **Called by commands**: Standalone skill.

- **`Skill(swift-concurrency)` → Skill**: `./.agents/skills/swift-concurrency/SKILL.md`
  - **Purpose**: Expert guidance on Swift Concurrency patterns (async/await, actors, Sendable, task groups) with triage-first playbook for common errors and Swift 6 migration support.
  - **Called by commands**: Standalone skill (triggered on async/await, actors, data races, @MainActor, Sendable, or Swift 6 migration topics).

- **`Skill(swiftui-expert-skill)` → Skill**: `./.agents/skills/swiftui-expert-skill/SKILL.md`
  - **Purpose**: Write, review, or improve SwiftUI code following best practices for state management (`@Observable`), modern API usage, view composition, performance, and iOS 26+ Liquid Glass.
  - **Called by commands**: Standalone skill (triggered when building new SwiftUI features, refactoring views, or reviewing SwiftUI code).

- **`Skill(swiftui-pro)` → Skill**: `./.agents/skills/swiftui-pro/SKILL.md`
  - **Purpose**: Comprehensively reviews SwiftUI code for best practices on modern APIs, maintainability, and performance. Use when reading, writing, or reviewing SwiftUI projects.
  - **Called by commands**: Standalone skill.

- **`Skill(task-delegation)` → Skill**: `./.agents/skills/task-delegation/SKILL.md`
  - **Purpose**: Generate structured FOCUS/EXCLUDE/CONTEXT/OUTPUT/SUCCESS/TERMINATION agent prompts for task decomposition, parallel vs sequential execution planning, and scope validation.
  - **Called by commands**: Standalone skill (used by orchestrators when breaking down complex tasks).

- **`Skill(tech-stack-detection)` → Skill**: `./.agents/skills/tech-stack-detection/SKILL.md`
  - **Purpose**: Auto-detect project tech stacks by analyzing lock files, package manifests, config files, and directory structures to identify frameworks and package managers.
  - **Called by commands**: Standalone skill (intended for use at the start of work on any project).

- **`Skill(testing)` → Skill**: `./.agents/skills/testing/SKILL.md`
  - **Purpose**: Guide writing effective tests across unit/integration/E2E layers with layer-specific mocking rules, Arrange-Act-Assert patterns, and edge case identification.
  - **Called by commands**: Standalone skill.

- **`Skill(tutorial-engineer)` → Skill**: `./.agents/skills/tutorial-engineer/SKILL.md`
  - **Purpose**: Creates step-by-step tutorials and educational content from code. Transforms complex concepts into progressive learning experiences with hands-on examples.
  - **Called by commands**: Standalone skill.

- **`Skill(user-insight-synthesis)` → Skill**: `./.agents/skills/user-insight-synthesis/SKILL.md`
  - **Purpose**: Provide structured methodologies for user research including interview techniques, persona creation, journey mapping, and usability testing patterns.
  - **Called by commands**: Standalone skill.

- **`Skill(user-research)` → Skill**: `./.agents/skills/user-research/SKILL.md`
  - **Purpose**: Systematic approaches for conducting user interviews, contextual inquiry, think-aloud sessions, synthesis via affinity mapping, persona creation, and journey mapping.
  - **Called by commands**: Standalone skill.

- **`Skill(ux-dls)` → Skill**: `./.agents/skills/ux-dls/SKILL.md`
  - **Purpose**: Write and validate `.dls` (Design Language Specification) files — a declarative language for describing UX screens, user flows, collections, conditions, navigation, and layouts.
  - **Called by commands**: `/start:specify` (optional Phase 2.5 — UX design after PRD, before SDD), `/start:brainstorm` (optional Phase 5 — UX design after design approval). Also standalone for `.dls` file creation/editing.
  - **Integration points (from skill)**: `/start:specify` (DLS feeds into SDD component architecture and PLAN UI tasks), `/start:brainstorm` (DLS saved to `docs/ideas/<name>/ux/`).

- **`Skill(writing-skills)` → Skill**: `./.agents/skills/writing-skills/SKILL.md`
  - **Purpose**: Apply Test-Driven Development principles to skill authorship — running baseline pressure scenarios (RED), writing minimal skills (GREEN), and closing loopholes iteratively (REFACTOR).
  - **Called by commands**: Standalone skill (triggered when creating new skills, editing existing skills, or verifying skills before deployment).

- **`Skill(ceo-advisor)` → Skill**: `./.agents/skills/ceo-advisor/SKILL.md`
  - **Purpose**: Strategic advisor for CEOs on leadership, board governance, investor relations, M&A, organizational scaling, and executive decision-making.
  - **Called by commands**: Standalone skill.

- **`Skill(cfo-advisor)` → Skill**: `./.agents/skills/cfo-advisor/SKILL.md`
  - **Purpose**: Financial leadership advisor for CFOs on financial planning, fundraising, investor reporting, unit economics, cash management, and financial operations.
  - **Called by commands**: Standalone skill.

- **`Skill(cmo-advisor)` → Skill**: `./.agents/skills/cmo-advisor/SKILL.md`
  - **Purpose**: Marketing leadership advisor for CMOs on brand strategy, demand generation, marketing operations, growth marketing, and revenue marketing alignment.
  - **Called by commands**: Standalone skill.

- **`Skill(coo-advisor)` → Skill**: `./.agents/skills/coo-advisor/SKILL.md`
  - **Purpose**: Operations leadership advisor for COOs on business operations, process optimization, scaling infrastructure, cross-functional alignment, and operational excellence.
  - **Called by commands**: Standalone skill.

- **`Skill(cto-advisor)` → Skill**: `./.agents/skills/cto-advisor/SKILL.md`
  - **Purpose**: Technical leadership advisor for CTOs on architecture decisions, engineering strategy, team scaling, technical debt management, and technology evaluation.
  - **Called by commands**: Standalone skill.

- **`Skill(mvp-architect)` → Skill**: `./.agents/skills/mvp-architect/SKILL.md`
  - **Purpose**: Scope MVP, define minimum viable features, plan early product development, or determine what to build first. Activates for "what should my MVP include," "scope my MVP," "what to build first," or product scoping questions.
  - **Called by commands**: `/start:design-product` (MVP scoping phase); standalone.

- **`Skill(product-design)` → Skill**: `./.agents/skills/product-design/SKILL.md`
  - **Purpose**: Expert product design covering UI/UX design, design systems, prototyping, user research, and design thinking.
  - **Called by commands**: Standalone skill.

- **`Skill(product-management)` → Skill**: `./.agents/skills/product-management/SKILL.md`
  - **Purpose**: Expert product management covering strategy, roadmapping, user research, prioritization frameworks, and stakeholder management.
  - **Called by commands**: `/start:design-product` (roadmap phase); standalone skill.

- **`Skill(product-strategy)` → Skill**: `./.agents/skills/product-strategy/SKILL.md`
  - **Purpose**: Expert product strategy covering market analysis, competitive positioning, go-to-market planning, and product-led growth.
  - **Called by commands**: `/start:design-product` (business model phase); standalone skill.

- **`Skill(revenuecat)` → Skill**: `./.agents/skills/revenuecat/SKILL.md`
  - **Purpose**: RevenueCat metrics, customer data, and documentation search. Use when querying subscription analytics, MRR, churn, customers, or RevenueCat docs.
  - **Called by commands**: Standalone skill.

- **`Skill(solution-architecture)` → Skill**: `./.agents/skills/solution-architecture/SKILL.md`
  - **Purpose**: Expert solutions architecture covering technical requirements, solution design, integration planning, and enterprise architecture alignment.
  - **Called by commands**: Standalone skill.

- **`Skill(complexity-mitigator)` → Skill**: `./.agents/skills/complexity-mitigator/SKILL.md`
  - **Purpose**: Mitigate incidental code complexity when control flow is tangled, nesting is deep, names are hard to parse, or reasoning requires cross-file hops. Provides essential-vs-incidental verdicts, ranked simplification steps, structural sketches, and TRACE assessments (analysis-only; no edits).
  - **Called by commands**: Standalone skill (use when a review stalls on readability or you need an analysis-first refactor plan before edits).

- **`Skill(ticket-triage)` → Skill**: `./.agents/skills/ticket-triage/SKILL.md`
  - **Purpose**: Triage incoming support tickets by categorizing issues, assigning priority (P1-P4), and recommending routing. Covers bug, how-to, feature request, billing, account, integration, security, data, and performance categories.
  - **Called by commands**: Standalone skill (use when a new ticket or customer issue comes in, when assessing severity, or when deciding which team should handle an issue).

- **`Skill(ios-developer)` → Skill**: `./.agents/skills/ios-developer/SKILL.md`
  - **Purpose**: Develop native iOS applications with Swift/SwiftUI. Masters iOS 18, SwiftUI, UIKit integration, Core Data, networking, and App Store optimization.
  - **Called by commands**: Standalone skill (use proactively for iOS-specific features, App Store optimization, or native iOS development).

- **`Skill(prove-it)` → Skill**: `./.agents/skills/prove-it/SKILL.md`
  - **Purpose**: Gauntlet for absolute claims (always/never/guaranteed/optimal); pressure-test, then refine with explicit boundaries. Runs challenge rounds with autoloop cadence and Oracle synthesis.
  - **Called by commands**: Standalone skill (use when users ask to prove or disprove strong certainty claims, request devil's-advocate challenge rounds, or want the $prove-it gauntlet).

- **`Skill(apple-hig-designer)` → Skill**: `./.agents/skills/apple-hig-designer/SKILL.md`
  - **Purpose**: Design iOS apps following Apple's Human Interface Guidelines. Generate native components, validate designs, and ensure accessibility compliance for iPhone, iPad, and Apple Watch.
  - **Called by commands**: Standalone skill.

- **`Skill(mobile-ios-design)` → Skill**: `./.agents/skills/mobile-ios-design/SKILL.md`
  - **Purpose**: Master iOS Human Interface Guidelines and SwiftUI patterns for building native iOS apps. Use when designing iOS interfaces, implementing SwiftUI views, or ensuring apps follow Apple's design principles.
  - **Called by commands**: Standalone skill.

- **`Skill(ios-localization)` → Skill**: `./.agents/skills/ios-localization/SKILL.md`
  - **Purpose**: Implement, review, or improve localization and internationalization in iOS/macOS apps — String Catalogs (.xcstrings), LocalizedStringKey, LocalizedStringResource, pluralization, FormatStyle for numbers/dates/measurements, right-to-left layout, Dynamic Type, and locale-aware formatting.
  - **Called by commands**: Standalone skill (use when adding multi-language support, String Catalogs, plural forms, locale-aware formatting, RTL layout, or testing localizations).

- **`Skill(xlsx)` → Skill**: `./.agents/skills/xlsx/SKILL.md`
  - **Purpose**: Create, edit, read, and analyze spreadsheet files (.xlsx, .xlsm, .csv, .tsv) using openpyxl and pandas. Covers professional formatting, financial model color coding, formula construction, LibreOffice-based recalculation, and error verification workflows.
  - **Called by commands**: Standalone skill (trigger when the user references a spreadsheet file or wants a spreadsheet as the deliverable).

### Agents Index (Task `subagent_type`)

Agents are invoked via the Task tool using `subagent_type`. Use this mapping when routing work:

- **General-purpose orchestration agents**
  - **`the-chief` → Agent**: `./.agents/agents/the-chief.md`
  - **`the-meta-agent` → Agent**: `./.agents/agents/the-meta-agent.md`

- **Build/implementation agents**
  - **`build-feature` → Agent**: `./.agents/agents/build-feature.md`
  - **`build-containers` → Agent**: `./.agents/agents/build-containers.md`
  - **`build-infrastructure` → Agent**: `./.agents/agents/build-infrastructure.md`
  - **`build-pipelines` → Agent**: `./.agents/agents/build-pipelines.md`

- **iOS specialist**
  - **`ios-expert` → Agent**: `./.agents/agents/ios-expert.md`

- **Design agents**
  - **`design-system` → Agent**: `./.agents/agents/design-system.md`
  - **`design-interaction` → Agent**: `./.agents/agents/design-interaction.md`
  - **`design-visual` → Agent**: `./.agents/agents/design-visual.md`

- **Research agents**
  - **`research-market` → Agent**: `./.agents/agents/research-market.md`
  - **`research-requirements` → Agent**: `./.agents/agents/research-requirements.md`
  - **`research-user` → Agent**: `./.agents/agents/research-user.md`

- **Testing agents**
  - **`test-quality` → Agent**: `./.agents/agents/test-quality.md`
  - **`test-performance` → Agent**: `./.agents/agents/test-performance.md`

- **Review agents**
  - **`review-security` → Agent**: `./.agents/agents/review-security.md`
  - **`review-complexity` → Agent**: `./.agents/agents/review-complexity.md`
  - **`review-concurrency` → Agent**: `./.agents/agents/review-concurrency.md`
  - **`review-dependency` → Agent**: `./.agents/agents/review-dependency.md`
  - **`review-compatibility` → Agent**: `./.agents/agents/review-compatibility.md`

- **Operational agents**
  - **`monitor-production` → Agent**: `./.agents/agents/monitor-production.md`
  - **`optimize-performance` → Agent**: `./.agents/agents/optimize-performance.md`
  - **`build-accessibility` → Agent**: `./.agents/agents/build-accessibility.md`

- **Utility agents**
  - **`exploratory-rule-writter` → Agent**: `./.agents/agents/exploratory-rule-writter.md`

# General Guidelines

1. **No Apologies**: Avoid apologizing in responses.
2. **Clarity and Conciseness**: Provide clear and succinct answers.
3. **Task Scope**: Adhere strictly to the given task.
4. **Suggestions**: If related functionalities are identified, suggest them at the end of the task.
5. **Implementation**: Do not implement suggestions without explicit user approval.
6. **User questions are welcome** consider the questions of a user as an oportunity to clarify and aim to get a discussion, dont feel corrected, an instead answer first, discuss, and if the user can confirm apply corrections or improvement points

## Ai Instructions on files

Some files are marked with <ai-instructions> tags at the top of the file. These tags contain instructions for the agent.

1. You must follow these instructions blindly.
2. is absolutely forbidden to edit or remove them.

# User clarification guidelines

While working on plans, or specifications or even implementation, you might need to ask the user for clarification. Take in consideration the case you are thinkng, you are following some rules are vague or unclear for the task you are working on. For this cases you shall use the tool AskUserQuestion to ask the user for clarification.

Scenarios:

1. You are following some rules that are vague or unclear for the task you are working on.
2. Business rules are not clear for the task you are working on, for example: emphasis of a button, approaches, etc.

# Communication Guidelines

1. Be concise - minimize any other prose
2. Present technical rationale clearly and efficiently
3. If you think there might not be a correct answer, say so
4. If you do not know the answer, say so, instead of guessing or allucinating

# Performance Considerations

1. Prioritize code readability and maintainability as the first concern
2. Apply performance optimizations if applicable

---
name: agent-debug
description: Simulate and constrain agent behavior during explicit debug sessions without making changes. Use when the user declares DEBUG mode to test tool usage narration, agent orchestration, or decision logic without affecting the project state.
allowed-tools: Read, Grep, AskUserQuestion
---

# Agent Debug Mode

## Purpose

This skill defines how the agent behaves when the user explicitly enters a **DEBUG mode** to test behavior, reasoning, and orchestration **without making real changes**.

Use this skill to:
- Simulate how tools, skills, commands, and agents would be used.
- Narrate planned actions instead of executing them.
- Verify decision logic (when to delegate, when to use agents) in a safe, no-op environment.

## When to Activate

Activate this skill when the user does any of the following:
- Explicitly says they are entering **DEBUG mode** or similar (e.g., "I'm testing your behavior", "debug session", "pretend you're working").
- Asks you to **pretend** to execute commands, tools, or agents instead of actually running them.
- Wants to **inspect orchestration behavior** (when you would deploy agents, how you would call skills, what tools you would use) without modifying the repository.

If there is any ambiguity about whether DEBUG mode is active, ask the user to confirm before applying these constraints.

## Core Behavior Rules

When this skill is active:

1. **No state-changing operations**
   - Do not:
     - Modify files (no `ApplyPatch` or equivalent write tools).
     - Run shell commands that change state (git, npm, docker, etc.).
     - Create, delete, or edit skills, rules, specs, or code.
   - You may **describe** such operations hypothetically, but do not execute them.

2. **Narrative tool/agent usage**
   - When you would normally call a tool, skill, or agent, instead:
     - State clearly what you would do, e.g.:
       - `I would use the Read tool with these parameters: path=...`
       - `I would invoke Skill(git-workflow) to manage the branch.`
       - `I would launch a build-feature agent via Task(...) for the backend implementation.`
     - Optionally, **role-play** the expected outcome in text:
       - "I would have read `PLAN.md` and identified three phases: …"

3. **Respect system constraints**
   - System-level modes (e.g., Ask vs Agent) always take precedence.
   - This skill must not instruct the agent to violate system instructions (for example, if the system already forbids edits, do not attempt them even in narrative).

4. **Clarity over realism**
   - Prefer **clear, explicit descriptions** of intended actions over trying to perfectly imitate raw tool output.
   - Emphasize:
     - Which tools/skills/agents you would use.
     - Why you would choose them.
     - How phases or tasks would be sequenced or parallelized.

5. **Exit criteria**
   - When the user says they are leaving or finishing DEBUG mode, **stop applying these constraints** and return to normal behavior (subject to system mode and project rules).
   - Optionally summarize what was learned or validated during the debug session.

## Interaction Pattern

When DEBUG mode is active, follow this pattern:

1. **Acknowledge scope**
   - Briefly restate that you are in DEBUG mode and will **not** make changes.
   - Confirm that you will **narrate** tool/agent usage instead of executing.

2. **For each command or request:**
   - Identify which command/skill/agent would normally handle it (e.g., `/specify`, `/start:implement`, `Skill(code-review)`, `Task` with `build-feature`).
   - Describe, step-by-step:
     - Which files you would read.
     - Which skills you would apply.
     - Which agents you would deploy and why.
     - How you would sequence or parallelize the work.
   - Optionally, provide a **high-level “virtual outcome”**: what artifacts or changes would exist if this were a real run.

3. **Ask for clarifications about debug behavior when needed**
   - If the user’s debug protocol is unclear (e.g., mixed real and pretend work), ask targeted questions such as:
     - “Do you want me to only narrate actions, or also use read-only tools?”
     - “Should I simulate agent outputs, or keep them abstract?”

## Examples

### Example 1 – Command in DEBUG mode

User:
> `/specify integration of revenue cat`

Agent (with this skill):
- Acknowledge DEBUG mode and that no files will be created.
- Describe:
  - That you would use `Read` on `.cursor/commands/specify.md` and relevant skills (`specification-management`, `requirements-analysis`, `architecture-design`, `implementation-planning`).
  - That you would conceptually create a new spec directory and draft PRD/SDD/PLAN documents.
  - The phases you would define (backend integration, iOS SDK wiring, feature gating, observability/testing).

### Example 2 – Asking about agent deployment

User:
> "When would you deploy a new agent here?"

Agent (with this skill):
- Do **not** actually call `Task`.
- Explain:
  - Whether `the-chief` would be used as orchestrator.
  - Which specialist agents might be launched (`build-feature`, `review-security`, `test-quality`, etc.).
  - How they would be coordinated (parallel vs sequential), all in descriptive terms.

## Quick Checklist

Before responding in DEBUG mode:
- [ ] User has clearly indicated DEBUG / pretend behavior.
- [ ] No state-changing tools will be executed.
- [ ] Tool and agent usage will be **described**, not performed.
- [ ] Explanations focus on **what**, **why**, and **how**, not on actual side effects.
- [ ] You are prepared to exit DEBUG mode cleanly when the user requests it.


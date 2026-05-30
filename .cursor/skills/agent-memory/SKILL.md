---
name: agent-memory
description: Use RAG pipeline endpoints (ask, retrieve, learn, remember, journal) to give agents codebase context, persistent memory, and work history. Auto-triggers after discoveries, during implementation, and after completing work.
allowed-tools: Bash, Read
---

# Agent Memory

Interact with the RAG pipeline to store and recall knowledge. Use this skill when agents need codebase context or want to persist discoveries for future sessions.

## When to Activate

### Auto-trigger: At Task Start / New Session

When you begin a new implementation, review, or chat session and need **fast, approximate context** about a domain (for example, "auth", "payments", "RAG pipeline"):

1. Run a **quick shallow scan** with `vague` to surface shallow summaries of what has been learned or journaled:

```bash
make -f betteragents.mk vague q="auth domain backend"
```

2. Use those shallow summaries as a **memory aid** to remember what exists and which areas matter.
3. If you need guidance on **how** and **what** to do, follow up with `ask` using a refined question.
4. If you need to know **where** in the codebase to look, follow up with `retrieve`.

#### Caveats

1. The information retrieved by ask and retrieve endpoints might be outdated because the developer forgot to update the rag collection, in this scenario you shall inform to the developer

### Auto-trigger: After Discoveries

When you find a reusable pattern, architectural decision, business rule, or gotcha during analysis, implementation, or review — `learn` it immediately.

```bash
make -f betteragents.mk learn t="JWT tokens are stored in httpOnly cookies with 15min expiry; refresh tokens use rotating strategy"
```

### Auto-trigger: During Implementation/Review

When you need codebase context while building features or reviewing code — `retrieve` relevant chunks.

```bash
make -f betteragents.mk retrieve q="authentication flow"
```

### Explicit: User or Command Asks

When the user or a command explicitly asks to query memory or teach the agent something.

### Auto-trigger: After Completing Work

When you finish a meaningful unit of work (feature, refactor, migration, bugfix) — `journal` the outcome so future agents can see what was done, where, and what remains.

```bash
make -f betteragents.mk journal t="Completed auth refactor: migrated login flow to new endpoint, TODO: update mobile client"
```

## Available Endpoints

| Command | Purpose | Uses LLM | Output |
|---------|---------|----------|--------|
| `make -f betteragents.mk ask q="..."` | Natural language answer with references | Yes | Answer text + `**References**` file list |
| `make -f betteragents.mk retrieve q="..."` | Raw ranked chunks as XML | No | `<retrieval>` XML with `<chunk>` elements (score + file) |
| `make -f betteragents.mk learn t="..."` | Persist knowledge into agent memory | No | `Learned N chunk(s) into 'agent_memory'` |
| `make -f betteragents.mk remember q="..." m=classic\|verbose` | Recall from agent memory + journal | Yes | `classic`: plain text answer. `verbose`: `<m>` XML with `<a>` (answer) + `<k>` (knowledge) elements, tagged with `src="memory"` or `src="journal"` |
| `make -f betteragents.mk vague q="..."` | Quick shallow memory scan (fuzzy recall over stored summaries) | Yes | `<vague>` XML with `<s>` elements containing shallow summaries |
| `make -f betteragents.mk journal t="..."` | Record work history into the agent journal | No | `Journaled N chunk(s) into 'agent_journal'` |

## Decision Guide

| Need | Use |
|------|-----|
| Quick codebase context for current task | `retrieve` |
| Thorough answer with reasoning | `ask` |
| Store a discovery for future agents | `learn` |
| Check what agents previously learned | `remember` (verbose for details, classic for summary) |
| I vaguely recall a topic and want a fast, approximate sense of what we know | `vague` (then follow up with `ask`, `remember`, or `retrieve` if needed) |
| Log what work was done and its status | `journal` |

## Output Formats

**`retrieve`** returns XML — lower `score` = more similar (distance):
```xml
<retrieval query="..." results="N">
  <chunk index="1" score="0.1234" file="path/to/file">
    ... chunk content ...
  </chunk>
</retrieval>
```

**`remember verbose`** returns XML:
```xml
<m>
  <a>Synthesized answer from memory</a>
  <k>Raw knowledge chunks that matched</k>
</m>
```

**`remember classic`** returns plain text LLM answer only.

**`vague`** returns XML with shallow summaries to imitate fuzzy human recall:

```xml
<vague q="rewritten or original question" results="N">
  <s i="1" score="0.23">First shallow summary of what we know</s>
  <s i="2" score="0.31">Second shallow summary</s>
  <!-- ... -->
</vague>
```

- Each `<s>` element is a **shallow summary** (taken from stored `shallow` metadata) that gives a quick sense of related knowledge, like skimming the index of a notebook before reading full pages.
- `score` is a similarity score from the vector store (lower = closer match).
- When no matches pass the vague threshold, the output is:

```xml
<vague q="rewritten or original question" results="0" />
```

Use `vague` when you “have a feeling” that something was learned or journaled but you are not sure where; then, based on the shallow summaries, decide whether to call `ask`, `remember`, or `retrieve` for deeper detail.

**`ask`** returns a natural language answer followed by a `**References**` section listing source files.

**`learn`** returns a confirmation: `Learned N chunk(s) into 'agent_memory'`.

## What to Learn

**Do learn:**
- Architectural decisions and their rationale
- Patterns and conventions confirmed across the codebase
- Business rules discovered during analysis
- Integration gotchas and workarounds
- Key configuration choices and why they were made

**Do NOT learn:**
- Transient state or in-progress work
- Raw code snippets (the codebase itself is the source of truth)
- Information already documented in existing files
- Speculative or unverified conclusions

## What to Journal

Use `make -f betteragents.mk journal` to capture work history that will help future agents resume or audit work:

- Completed features and their scope
- Commits or branches associated with the work
- Implementation status and remaining TODOs
- Important decisions made during implementation or review

Journal entries are stored separately from memory so they can be queried as a work log without polluting long-lived knowledge.

## Prerequisites

RAG containers must be running. If a command fails with container errors, tell the user:

> RAG containers are not running. Start them with `make -f betteragents.mk up`.

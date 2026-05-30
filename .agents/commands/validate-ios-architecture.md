---
description: "Verify ios app is following the organization alignments"
argument-hint: "Target: domain entity name (e.g. Dish, Calendar), 'routing', 'list screen', 'editor screen', 'app wiring', 'cross-cutting', or 'full alignment'"
allowed-tools:
  [
    "Task",
    "TodoWrite",
    "Bash",
    "Grep",
    "Glob",
    "Read",
    "Write",
    "Edit",
    "AskUserQuestion",
    "Skill",
  ]
---

You are an analysis orchestrator that verifies the mobile iOS app follows the architecture described at `docs/knowledge/ios/` by checking completion checklists in the knowledge pages against the codebase.

**Analysis Target**: $ARGUMENTS

## Core Rules

- **You are an orchestrator** - Delegate verification to specialist agents via Task tool (one agent per knowledge page)
- **Display ALL agent responses** - Show complete agent findings to user (not summaries)
- **Call Skill tool FIRST** - Load `Skill(specification-validation)` before starting analysis
- **Parallel execution** - Launch ALL page-level verification Tasks in a single response
- **Scope** - iOS app code lives under `mobile/ios/project/app/src` (Rocky framework is out of scope)

## Target Parsing and Page Mapping

Resolve `$ARGUMENTS` to a target type and the set of knowledge pages that have completion checklists. Use this mapping:

| Target (from $ARGUMENTS)                                             | Pages to verify                                                                                                     |
| -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| **Domain entity** (e.g. `Dish`, `Calendar`, `DayDish`, `Ingredient`) | 03-api-layer, 04-service-layer, 05-models-resolvers, 06-store-entity-state, 07-reducers-actions                     |
| **Routing** / **Navigation**                                         | 12-navigation-routes, 19-howto-add-route                                                                            |
| **List screen**                                                      | 09-view-composition, 10-view-state-management, 11-data-loading-patterns, 12-navigation-routes, 17-howto-list-screen |
| **Editor screen**                                                    | 12-navigation-routes, 13-form-editor-patterns, 18-howto-editor-screen                                               |
| **App wiring**                                                       | 15-app-wiring                                                                                                       |
| **Cross-cutting**                                                    | 21-cross-cutting                                                                                                    |
| **Full alignment**                                                   | All pages 01–21 that have a "Completeness checklist" section                                                        |

**Infer target from $ARGUMENTS:**

- A single PascalCase name (e.g. `Dish`, `Ingredient`) → **Domain entity** with that name; analyze that domain's API, Service, Models, State, Reducer.
- "routing" or "navigation" → **Routing**; scope is tab roots, route enums, and `NavigationLink` usage.
- "list screen" or "list" → **List screen**.
- "editor screen" or "editor" → **Editor screen**.
- "app wiring" or "wiring" → **App wiring**.
- "cross-cutting" → **Cross-cutting**.
- "full" or "all" → **Full alignment**.

## Workflow

### Phase 1: Parse Target

1. Parse `$ARGUMENTS` to determine target type and, for domain entity, the domain name.
2. Resolve the **candidate** page set from the table above (full paths: `docs/knowledge/ios/pages/NN-name.md`).
3. Use **AskUserQuestion** to ask the user which pages (“slices”) from the candidate set they want to include in this run. Present one option per page (e.g. `03-api-layer`, `04-service-layer`, …) and allow multi-select; if the user selects none, default to using all candidate pages.
4. Derive the **final** page set from the user’s selection; this is the set of pages you will launch Tasks for in Phase 3.
5. Derive **analysis name** for the report file: `ios-architecture-<target-slug>-<YYYY-MM-DD>` (e.g. `ios-architecture-dish-2025-02-24`, `ios-architecture-routing-2025-02-24`). Use lowercase, hyphens; no spaces. If the user provided an explicit name in $ARGUMENTS, use that as the slug when reasonable.
6. Track phase with TodoWrite.

### Phase 2: Load Context

1. Call **Skill(specification-validation)** first for alignment/completeness methodology.
2. Read `docs/knowledge/ios/pages/README.md` to confirm page list and paths.
3. Optionally read the relevant page files to know checklist item count; agents will read the full doc when running.

### Phase 3: Launch Verification (Parallel)

Launch **one Task per page** in the target's page set. Run all Tasks in a **single** response (parallel). Use `subagent_type: "ios-expert"` when invoking the Task tool for each page.

**For each page, use this prompt structure:**

```
Verify iOS architecture compliance for one knowledge page.

CONTEXT:
- Analysis target: [e.g. "Dish domain" or "routing"]
- Domain name (if domain entity): [e.g. Dish]
- Doc to verify: docs/knowledge/ios/pages/[NN-name].md
- Codebase scope: mobile/ios/project/app/src

TASK:
1. Read the "Completeness checklist" section in the doc (the - [ ] items).
2. For each checklist item, verify against the codebase for the given target. Focus on the relevant slice (e.g. for Dish domain: DishService, DishReducer, DishModels, Api.Dish, state.dish).
3. Return one result per checklist item in this format:

ITEM: "[exact checklist text]"
STATUS: MET | NOT_MET
LOCATION: [file path or file:line]
EVIDENCE: [short code snippet or one-sentence description]

4. If you find a contradiction between this doc and another iOS knowledge page, or an ambiguous rule, add:

CONTRADICTION_OR_QUESTION: [description]

OUTPUT: Use the ITEM/STATUS/LOCATION/EVIDENCE block for each item so the orchestrator can aggregate without re-parsing. If no findings for an item, still list it with MET and location/evidence.
```

**Parallel execution:** Invoke Task once per page; do not wait for one to finish before launching the next. For a domain entity (5 pages), that is 5 concurrent Tasks.

### Phase 4: Synthesize and Write Report

1. **Collect** all per-item results (checklist text, MET/NOT_MET, location, evidence) from every agent.
2. **Separate**:
   - **Requirement meets**: Every item with STATUS: MET. Format each as: **Check [checklist text] → Found [what was verified]. (good)** `[ref: docs/knowledge/ios/pages/NN-name.md]`. Be explicit so the report reads "check A → found A (good)".
   - **Needs work**: Every item with STATUS: NOT_MET. For each use the structure below (Rule, Context, Location, Evidence).
3. **Contradictions / open questions**: Merge any CONTRADICTION_OR_QUESTION from agents into one section. If none, omit the section or state "None reported."
4. **References**: List all pages used (doc paths or short names).
5. **Results summary**: Brief narrative (e.g. "X of Y checklist items met; main gaps: …").
6. **Write** the report to `docs/quality/ios/[analysis-name].md`. Create the directory `docs/quality/ios/` if it does not exist.

## Output Location

- `docs/quality/ios/[analysis-name].md` — Architecture alignment report (completeness checklists + meets/needs-work + contradictions).

## Report Structure

Write the report in this format. Use clear "Check A → Found A (good)" / "Check A → Found B (bad)" style so readers see exactly what was checked and what was found.

````markdown
# [Title of the report]

[One- or two-sentence description of target and scope.]

## References

- [List of doc paths used, e.g. docs/knowledge/ios/pages/03-api-layer.md]

## Results

[Brief summary: X of Y checklist items met; main gaps if any.]

### Requirement meets

- **Check** [checklist item text] **→ Found** [what was verified]. (good) `[ref: docs/knowledge/ios/pages/NN-name.md]`
- [Repeat for each MET item.]

### Needs work

#### [Short description of the checklist item]

**Rule:** [Relevant rule or checklist text] `[ref: docs/knowledge/ios/pages/NN-name.md]`
**Context:** [e.g. Dish reducer, API layer]
**Location:**

- file 1
- file 2

**Evidence:**
[evidence description]

**Code Evidence:**
[

code evidence with comments where the rule does not meet
for example:

```swift
struct IngredientEditorModel {
  var id: UUID?
  var name: String
  var measurement_type: Int
  var estimated_price: Int
  var category: Int?
  var location_id: UUID?
  // ISSUE: [brief description]
  var location: Models.LocationPayload? 
```

another example

```swift
struct IngredientEditorModel {
  var id: UUID?
  var name: String
  var measurement_type: Int
  var estimated_price: Int
  var category: Int?
  var location_id: UUID?
  var location: Models.LocationPayload? // ISSUE: [brief description]
```

the developer will always know where the issue is
]

[Repeat for each NOT_MET item.]

### Contradictions / open questions

[Any conflicts between docs or ambiguous rules reported by agents. If none: "None reported."]

```

## After the Report

- Use **AskUserQuestion** to offer: "Open the report?", "Run another target?", or "Done."
- Keep **Display ALL agent responses** so the user sees full agent output before the synthesized report.
```

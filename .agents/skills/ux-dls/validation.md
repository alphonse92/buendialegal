# DLS Validation Checklist

Use this checklist to validate `.dls` file completeness before considering a UX spec done.

## Structure Validation

- [ ] **File has `.dls` extension** — Default location: `docs/dls/` (confirmed via AskUserQuestion)
- [ ] **Sections ordered correctly** — Data > Screens > Navigation > Layouts > Flows
- [ ] **Consistent indentation** — 4 spaces throughout
- [ ] **All constructs named** — PascalCase identifiers on every block

## Data Validation

- [ ] **Collections define Items** — Every Collection has at least one Item with fields
- [ ] **Conditions reference real Collections** — Computed fields use existing Collection.field paths
- [ ] **Condition triggers are clear** — `exceeded when` or equivalent is unambiguous

## Screen Validation

- [ ] **Every Screen has a Title**
- [ ] **States defined for data-dependent screens** — At minimum: Loading, Error
- [ ] **Empty state defined** — For screens showing lists or collections
- [ ] **All actions have `->` navigation** — No dead-end buttons
- [ ] **Destructive actions have confirmation** — `confirm Dialog { ... }` present
- [ ] **Alert conditions reference defined Conditions**
- [ ] **Variants documented** — If Variants listed, each has a `Variant Name { }` block

## Flow Validation

- [ ] **Every Flow has a name** — `Flow: FlowName { }`
- [ ] **Flow has clear entry point** — `From [Screen]`
- [ ] **Steps use `->` arrows** — Navigation is explicit
- [ ] **Flow has Outcome block** — States what changed in the UI
- [ ] **All referenced Screens exist** — No orphan screen references

## Navigation Validation

- [ ] **Tab labels are unique** — No duplicate tab names
- [ ] **Tab targets are defined Screens** — Every `-> View` points to a real Screen

## Consistency Checks

- [ ] **Screen names match across Flows and Navigation** — Same PascalCase name everywhere
- [ ] **Collection names match across Conditions and Screens** — Consistent references
- [ ] **No implementation details leaked** — No API endpoints, database columns, or code

## Completeness

- [ ] **A designer could build wireframes from this** — Enough detail for visual design
- [ ] **A developer could build the UI from this** — Screens, states, and flows are clear
- [ ] **A PM could validate requirements from this** — Business conditions and outcomes stated

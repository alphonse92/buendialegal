---
name: ux-dls
description: Use when writing or reviewing DLS (Design Language Specification) files that describe UX screens, user flows, data collections, conditions, navigation, or component layouts. Triggers on .dls file creation, editing, or when translating UX ideas into structured specifications.
---

# UX Design Language Specification (DLS)

You are a UX specification writer that creates and validates `.dls` files — a lightweight, structured language for describing user interfaces, flows, and business conditions.

## Overview

DLS is a declarative language for capturing UX intent. It describes **what** the user sees and **how** they navigate, not implementation details. Think of it as pseudocode for UX.

**Core principle:** Every `.dls` file should be readable by designers, developers, and product people without explanation.

## When to Use

- Describing a new screen or view
- Mapping a user flow end-to-end
- Defining business conditions that trigger UI behavior
- Specifying navigation structure
- Documenting data collections that back UI elements

**When NOT to use:**
- Implementation details (use code)
- Visual styling (use design tokens / Figma)
- API contracts (use OpenAPI)

## Language Reference

### Constructs

| Construct | Purpose | Example |
|-----------|---------|---------|
| `Collection` | Data structures backing UI | `Collection: Receipts { Item: Receipt { ... } }` |
| `Condition` | Business rules with triggers | `Condition: BudgetLimit { exceeded when X > Y }` |
| `Screen` | A full view/page | `ScreenName: Screen { Title, Content, States }` |
| `Flow` | End-to-end user journey | `Flow: CheckoutFlow { steps... Outcome: ... }` |
| `TabNavigation` | Tab-based navigation | `TabNavigation: BottomTabs { Tab: "Label" -> View }` |
| `Layout` | Layout container | `LayoutName: Layout(Column) { spacing, padding }` |
| `Dialog` | Confirmation/modal dialog | `Dialog { title, message, confirmLabel, style }` |

### Navigation Arrow (`->`)

The `->` operator describes transitions between states or screens:

```
PrimaryAction: "Add receipt"
    -> opens UploadReceiptScreen as modal

DestructiveAction: "Close session" {
    confirm Dialog { ... }
    result: returns to LoginScreen
}
```

### Screen Anatomy

```dls
ScreenName: Screen {

    Title: "Display title"

    Content:
        [UI elements, lists, cards]

    PrimaryAction: "Button label"
        -> [navigation target]

    DestructiveAction: "Danger label" {
        confirm Dialog { ... }
        result: [outcome]
    }

    States:
        Loading: shows Spinner
        Empty: shows EmptyState { message, PrimaryAction }
        Error: shows InlineMessage("Error text")
        Offline: shows Banner("No connection")

    Alert when [Condition].exceeded {
        style: toast
        variant: warning
        message: "Alert text"
    }

    Variants:
        VariantName
        AnotherVariant

    Variant VariantName {
        shows [alternative content]
    }
}
```

### Collection & Condition

```dls
Collection: CollectionName {
    Item: ItemName {
        field1
        field2
        field3
    }
}

Condition: ConditionName {
    limit
    computed = sum(CollectionName.field)
    exceeded when computed > limit
}
```

### Flow

```dls
Flow: FlowName {

    From SourceScreen
        -> taps "Action label"
        -> opens TargetScreen

    In TargetScreen
        -> [user action]
        -> enters [State]

    When [condition]
        -> [system response]
        -> returns to [Screen]

    Outcome:
        [what changed in the UI]
}
```

### Navigation

```dls
TabNavigation: BottomTabs {
    Tab: "Label1" -> View1
    Tab: "Label2" -> View2
    Tab: "Label3" -> View3
}
```

### Layout

```dls
LayoutName: Layout(Column) {
    spacing: 16
    padding: 24
    scrollable: true
    $children
}
```

## Template

See [template.md](template.md) for a starter `.dls` file structure.

## Validation

See [validation.md](validation.md) for the completeness checklist.

## Writing Guidelines

1. **One concept per block** — Don't mix unrelated screens in the same block
2. **Name everything** — Screens, flows, conditions all get named identifiers
3. **States are explicit** — Always define Loading, Empty, Error states for screens that fetch data
4. **Flows have outcomes** — Every flow must state what changed
5. **Actions declare navigation** — Every action uses `->` to show where it leads
6. **Conditions are computed** — Use `sum()`, `count()`, comparisons — keep it readable
7. **Indentation signals nesting** — Use consistent indentation (4 spaces)
8. **Order matters** — In a file: Collections first, then Conditions, then Screens, then Navigation/Layout, then Flows

## Saving DLS Files

**REQUIRED:** Before writing a `.dls` file, use `AskUserQuestion` to confirm the save location.

- Default path: `docs/project/dls/$name.dls`
- Suggest the name based on the primary flow or screen group
- Lowercase, hyphenated names: `upload-receipt.dls`, `settings-logout.dls`
- Files use `.dls` extension

**Example prompt:**
```
Question: "Where should I save this DLS file?"
Options:
  - "docs/project/dls/upload-receipt.dls (Recommended)"
  - "Custom path"
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Missing States on a Screen | Always include at least Loading and Error |
| Flow without Outcome | Add `Outcome:` block stating what changed |
| Action without `->` | Every action must declare its navigation target |
| Unnamed constructs | Give every Screen, Flow, Condition a PascalCase name |
| Implementation details in DLS | Remove API endpoints, database fields — keep it UX-level |
| Missing confirm on destructive actions | Wrap destructive actions with `confirm Dialog { ... }` |

## Examples

Reference the DLS files in this skill's examples directory:
- [examples/recipt.dls](examples/recipt.dls) — Receipt upload flow with collection, condition, and screens
- [examples/logout.dls](examples/logout.dls) — Settings, navigation, dashboard layout, and logout flow
- [examples/annotated-example.dls](examples/annotated-example.dls) — Fully annotated meal planning example

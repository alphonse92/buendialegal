# DLS Template

Use this template when creating a new `.dls` file. Remove sections that don't apply.

```dls
// ============================================
// [Feature Name] — UX Specification
// ============================================

// --- Data ---

Collection: [CollectionName] {
    Item: [ItemName] {
        [field1]
        [field2]
        [field3]
    }
}

Condition: [ConditionName] {
    [threshold_field]
    [computed_field] = [aggregation]([CollectionName].[field])
    exceeded when [computed_field] > [threshold_field]
}

// --- Screens ---

[ScreenName]: Screen {

    Title: "[Screen title]"

    Content:
        [UI elements]

    PrimaryAction: "[Button label]"
        -> [navigation target]

    States:
        Loading: shows Spinner
        Empty: shows EmptyState {
            message: "[Empty message]"
            PrimaryAction: "[Action label]"
        }
        Error: shows InlineMessage("[Error message]")
}

// --- Navigation ---

TabNavigation: [NavName] {
    Tab: "[Label]" -> [View]
}

// --- Layouts ---

[LayoutName]: Layout([Type]) {
    spacing: [number]
    padding: [number]
    scrollable: [true/false]
    $children
}

// --- Flows ---

Flow: [FlowName] {

    From [SourceScreen]
        -> taps "[Action label]"
        -> opens [TargetScreen]

    In [TargetScreen]
        -> [user action]
        -> enters [State]

    When [condition]
        -> [system response]
        -> returns to [Screen]

    Outcome:
        [description of what changed]
}
```

## Section Ordering

1. **Data** — Collections and Conditions
2. **Screens** — All screen definitions
3. **Navigation** — Tab bars, drawers, navigation structures
4. **Layouts** — Reusable layout containers
5. **Flows** — User journey specifications

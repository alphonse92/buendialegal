---
name: lsp-swift
description: 'Use the Swift LSP (SourceKit-LSP) for code intelligence in Swift projects. Use when: (1) navigating Swift codebases — go-to-definition, find references, symbol search, (2) understanding Swift types — hover for type info, documentation, (3) analyzing call hierarchies — who calls what, what calls whom, (4) listing symbols in Swift files or across the workspace, (5) finding protocol implementations, (6) debugging import or type resolution issues via LSP diagnostics.'
---

# Swift LSP (SourceKit-LSP)

## Overview

This skill enables agents to leverage the Swift Language Server Protocol (SourceKit-LSP) for deep code intelligence when working with Swift projects. It provides type-aware navigation, symbol search, call hierarchy analysis, and diagnostics that go beyond text-based grep/glob searches.

## When to Use

- **Navigating to definitions** — jump to where a Swift type, function, or property is declared
- **Finding all references** — locate every usage of a symbol across the project
- **Understanding types** — get type signatures, documentation, and inferred types via hover
- **Listing file symbols** — enumerate all structs, classes, enums, functions, properties in a file
- **Workspace-wide symbol search** — find symbols by name across the entire project
- **Finding protocol implementations** — locate concrete types that implement a protocol
- **Analyzing call hierarchies** — trace incoming/outgoing calls for a function or method
- **Verifying type resolution** — check if SourceKit-LSP can resolve types (diagnostics)

## When NOT to Use

- Text pattern searches
- File discovery
- Non-Swift files
- Build errors

## Prerequisites

### SourceKit-LSP Installation

SourceKit-LSP ships with Xcode. Verify it's available:

```bash
# Check if sourcekit-lsp is available
xcrun sourcekit-lsp --help
```

**If not installed:**

1. **Install Xcode** from the Mac App Store or Apple Developer portal
2. **Install Command Line Tools**: `xcode-select --install`
3. **Verify**: `xcrun sourcekit-lsp --help`

**If using Swift toolchain without Xcode:**

1. Download a Swift toolchain from [swift.org](https://swift.org/download/)
2. SourceKit-LSP is included in the toolchain
3. Verify: `sourcekit-lsp --help`

### Project Requirements

For best LSP results:

- **SwiftPM projects**: Ensure `Package.swift` exists and `swift build` succeeds at least once
- **Xcode projects**: Build the project at least once in Xcode so the index is populated
- **Mixed projects**: The `.build/` or derived data index helps SourceKit-LSP resolve cross-module references

> **Note**: SourceKit-LSP works best after a successful build. Without a build index, cross-module type resolution may show "Cannot find type in scope" diagnostics. These are expected and don't block navigation within the same module.

## Agent Behavior Contract

1. **Always specify absolute file paths** when calling LSP operations.
2. **Use 1-based line and character numbers** as they appear in editors (matching `Read` tool output line numbers).
3. **Start with `documentSymbol`** to orient yourself in a file before using positional operations like `hover` or `goToDefinition`.
4. **Interpret diagnostics carefully** — "Cannot find type in scope" often means the build index is stale, not that the code is wrong.
5. **Fall back to Grep/Glob** when LSP returns no results (e.g., for string literals, comments, or cross-module references without an index).
6. **Combine LSP with Read** — use LSP for navigation, then `Read` to examine the full context around the target.

## Operations Reference

### `documentSymbol` — List All Symbols in a File

Use to get an overview of a file's structure (classes, structs, enums, functions, properties).

```
LSP(operation: "documentSymbol", filePath: "/path/to/File.swift", line: 1, character: 1)
```

**When to use**: First operation when exploring an unfamiliar Swift file.

### `hover` — Get Type Info and Documentation

Use to inspect a symbol's type signature, inferred type, or attached documentation.

```
LSP(operation: "hover", filePath: "/path/to/File.swift", line: 10, character: 15)
```

**When to use**: To understand what a variable, function, or type resolves to.

### `goToDefinition` — Jump to Symbol Definition

Use to find where a type, function, or property is declared.

```
LSP(operation: "goToDefinition", filePath: "/path/to/File.swift", line: 10, character: 15)
```

**When to use**: To navigate from a usage to its declaration.

### `findReferences` — Find All Usages

Use to locate every reference to a symbol across the project.

```
LSP(operation: "findReferences", filePath: "/path/to/File.swift", line: 10, character: 15)
```

**When to use**: Before renaming, refactoring, or understanding impact of changes.

### `workspaceSymbol` — Search Symbols Across Project

Use to find symbols by name across the entire workspace.

```
LSP(operation: "workspaceSymbol", filePath: "/path/to/any/File.swift", line: 1, character: 1)
```

**When to use**: To locate a type or function when you know its name but not its file.

> **Note**: The `filePath` must point to a valid Swift file in the project for context, but the search is workspace-wide.

### `goToImplementation` — Find Protocol Implementations

Use to find concrete types that implement a protocol method or conform to a protocol.

```
LSP(operation: "goToImplementation", filePath: "/path/to/Protocol.swift", line: 5, character: 10)
```

**When to use**: To trace from a protocol definition to its concrete implementations.

### `prepareCallHierarchy` — Get Call Hierarchy Item

Use to prepare a call hierarchy item at a function/method position.

```
LSP(operation: "prepareCallHierarchy", filePath: "/path/to/File.swift", line: 10, character: 15)
```

**When to use**: As a prerequisite for `incomingCalls` or `outgoingCalls`.

### `incomingCalls` — Who Calls This Function?

Use to find all callers of a function or method.

```
LSP(operation: "incomingCalls", filePath: "/path/to/File.swift", line: 10, character: 15)
```

**When to use**: To understand the impact of changing a function, or to trace execution paths.

### `outgoingCalls` — What Does This Function Call?

Use to find all functions/methods called by a specific function.

```
LSP(operation: "outgoingCalls", filePath: "/path/to/File.swift", line: 10, character: 15)
```

**When to use**: To understand a function's dependencies and side effects.

## Common Workflows

### Workflow: Understand a Swift File

```
1. LSP(documentSymbol) → list all types, methods, properties
2. LSP(hover) on key symbols → understand types and signatures
3. Read the file for full context
```

### Workflow: Trace a Type's Usage

```
1. LSP(goToDefinition) → find where the type is declared
2. LSP(findReferences) → find all usages across the project
3. LSP(incomingCalls) on key methods → understand call chains
```

### Workflow: Understand Protocol Conformance

```
1. LSP(documentSymbol) on protocol file → list protocol requirements
2. LSP(goToImplementation) on each requirement → find concrete implementations
3. LSP(findReferences) → find where the protocol is used as a type constraint
```

### Workflow: Impact Analysis Before Refactoring

```
1. LSP(findReferences) → all usages of the target symbol
2. LSP(incomingCalls) → all callers of the target function
3. LSP(outgoingCalls) → all dependencies of the target function
4. Assess blast radius before making changes
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Cannot find type in scope" diagnostics | Stale or missing build index | Run `swift build` or build in Xcode |
| LSP returns no results for `goToDefinition` | Symbol is in another module without index | Build the project, then retry |
| `findReferences` misses some usages | Incomplete index | Do a clean build (`swift build` or Xcode Build) |
| LSP operations time out | Large project, first indexing | Wait for indexing to complete; check `sourcekit-lsp` process |
| No LSP server available error | SourceKit-LSP not installed/configured | Install Xcode or Swift toolchain (see Prerequisites) |

## Best Practices

1. **Build first** — Run `swift build` or build in Xcode before relying on LSP for cross-module navigation.
2. **Combine tools** — Use LSP for type-aware navigation, Grep for text patterns, Glob for file discovery.
3. **Check diagnostics** — LSP diagnostics reveal type resolution issues that may indicate missing imports or build problems.
4. **Use `documentSymbol` as entry point** — It gives you the map of a file without needing exact positions.
5. **Absolute paths** — Always use absolute file paths for reliable results.

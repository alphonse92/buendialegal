---
name: lsp-typescript
description: 'Use the TypeScript LSP (tsserver) for code intelligence in TypeScript and JavaScript projects. Use when: (1) navigating TS/JS codebases — go-to-definition, find references, symbol search, (2) understanding types — hover for type info, inferred types, generics resolution, (3) analyzing call hierarchies — who calls what, what calls whom, (4) listing symbols in TS/JS files or across the workspace, (5) finding interface implementations, (6) debugging type errors or import resolution issues via LSP diagnostics.'
---

# TypeScript LSP (tsserver)

## Overview

This skill enables agents to leverage the TypeScript Language Server Protocol (tsserver) for deep code intelligence when working with TypeScript and JavaScript projects. It provides type-aware navigation, symbol search, call hierarchy analysis, and diagnostics that go beyond text-based grep/glob searches.

## When to Use

- **Navigating to definitions** — jump to where a type, function, class, or variable is declared
- **Finding all references** — locate every usage of a symbol across the project
- **Understanding types** — get type signatures, inferred types, generic resolutions via hover
- **Listing file symbols** — enumerate all classes, interfaces, functions, variables, types in a file
- **Workspace-wide symbol search** — find symbols by name across the entire project
- **Finding interface implementations** — locate concrete classes that implement an interface
- **Analyzing call hierarchies** — trace incoming/outgoing calls for a function or method
- **Verifying type resolution** — check if tsserver can resolve types and imports (diagnostics)

## When NOT to Use

- Text pattern searches
- File discovery
- Non-TypeScript/JavaScript files
- Build errors

## Prerequisites

### TypeScript LSP (tsserver) Installation

tsserver is bundled with TypeScript. Verify it's available:

```bash
# Check if TypeScript is installed (tsserver comes with it)
npx tsc --version

# Or check globally
tsc --version
```

**If not installed:**

1. **Project-local (recommended)**:
   ```bash
   npm install --save-dev typescript
   # or
   yarn add --dev typescript
   # or
   pnpm add --save-dev typescript
   # or
   bun add --dev typescript
   ```

2. **Global installation**:
   ```bash
   npm install -g typescript
   ```

3. **Verify**: `npx tsc --version`

### Project Requirements

For best LSP results:

- **Ensure `tsconfig.json` exists** — tsserver uses it to understand project structure, paths, and compiler options
- **Install dependencies** — run `npm install` (or your package manager's install) so `node_modules` types are available
- **Check path aliases** — if using `paths` in `tsconfig.json`, ensure `baseUrl` is set correctly

> **Note**: tsserver works well even without a prior build, since it uses `tsconfig.json` for project configuration. However, missing `node_modules` will cause "Cannot find module" diagnostics.

## Agent Behavior Contract

1. **Always specify absolute file paths** when calling LSP operations.
2. **Use 1-based line and character numbers** as they appear in editors (matching `Read` tool output line numbers).
3. **Start with `documentSymbol`** to orient yourself in a file before using positional operations like `hover` or `goToDefinition`.
4. **Interpret diagnostics carefully** — "Cannot find module" usually means `npm install` hasn't been run, not that the code is wrong.
5. **Fall back to Grep/Glob** when LSP returns no results (e.g., for dynamic imports, string-based references, or untyped JS files).
6. **Combine LSP with Read** — use LSP for navigation, then `Read` to examine the full context around the target.
7. **Works for both `.ts` and `.js` files** — tsserver provides intelligence for JavaScript files too (especially with JSDoc annotations or `checkJs` enabled).

## Operations Reference

### `documentSymbol` — List All Symbols in a File

Use to get an overview of a file's structure (classes, interfaces, functions, variables, types).

```
LSP(operation: "documentSymbol", filePath: "/path/to/file.ts", line: 1, character: 1)
```

**When to use**: First operation when exploring an unfamiliar TypeScript file.

### `hover` — Get Type Info and Documentation

Use to inspect a symbol's type signature, inferred type, JSDoc documentation, or generic resolution.

```
LSP(operation: "hover", filePath: "/path/to/file.ts", line: 10, character: 15)
```

**When to use**: To understand what a variable, function, or type resolves to — especially useful for inferred types and generics.

### `goToDefinition` — Jump to Symbol Definition

Use to find where a type, function, class, or variable is declared.

```
LSP(operation: "goToDefinition", filePath: "/path/to/file.ts", line: 10, character: 15)
```

**When to use**: To navigate from a usage to its declaration, including into `node_modules` type definitions (`.d.ts` files).

### `findReferences` — Find All Usages

Use to locate every reference to a symbol across the project.

```
LSP(operation: "findReferences", filePath: "/path/to/file.ts", line: 10, character: 15)
```

**When to use**: Before renaming, refactoring, or understanding impact of changes.

### `workspaceSymbol` — Search Symbols Across Project

Use to find symbols by name across the entire workspace.

```
LSP(operation: "workspaceSymbol", filePath: "/path/to/any/file.ts", line: 1, character: 1)
```

**When to use**: To locate a type or function when you know its name but not its file.

> **Note**: The `filePath` must point to a valid TS/JS file in the project for context, but the search is workspace-wide.

### `goToImplementation` — Find Interface Implementations

Use to find concrete classes that implement an interface or abstract method.

```
LSP(operation: "goToImplementation", filePath: "/path/to/interface.ts", line: 5, character: 10)
```

**When to use**: To trace from an interface or abstract class to its concrete implementations.

### `prepareCallHierarchy` — Get Call Hierarchy Item

Use to prepare a call hierarchy item at a function/method position.

```
LSP(operation: "prepareCallHierarchy", filePath: "/path/to/file.ts", line: 10, character: 15)
```

**When to use**: As a prerequisite for `incomingCalls` or `outgoingCalls`.

### `incomingCalls` — Who Calls This Function?

Use to find all callers of a function or method.

```
LSP(operation: "incomingCalls", filePath: "/path/to/file.ts", line: 10, character: 15)
```

**When to use**: To understand the impact of changing a function, or to trace execution paths.

### `outgoingCalls` — What Does This Function Call?

Use to find all functions/methods called by a specific function.

```
LSP(operation: "outgoingCalls", filePath: "/path/to/file.ts", line: 10, character: 15)
```

**When to use**: To understand a function's dependencies and side effects.

## Common Workflows

### Workflow: Understand a TypeScript File

```
1. LSP(documentSymbol) → list all types, classes, functions, exports
2. LSP(hover) on key symbols → understand types, generics, inferred types
3. Read the file for full context
```

### Workflow: Trace a Type's Usage

```
1. LSP(goToDefinition) → find where the type is declared
2. LSP(findReferences) → find all usages across the project
3. LSP(incomingCalls) on key methods → understand call chains
```

### Workflow: Understand Interface Implementations

```
1. LSP(documentSymbol) on interface file → list interface members
2. LSP(goToImplementation) on each member → find concrete implementations
3. LSP(findReferences) → find where the interface is used as a type
```

### Workflow: Debug Import/Type Resolution

```
1. LSP(hover) on the problematic import or type → check if tsserver resolves it
2. LSP(goToDefinition) on the import → verify it points to the right file
3. Check diagnostics for "Cannot find module" or type errors
4. If unresolved: verify tsconfig.json paths, run npm install, check node_modules
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
| "Cannot find module" diagnostics | Missing `node_modules` | Run `npm install` (or your package manager) |
| LSP returns no results for `goToDefinition` | Symbol is dynamically generated or untyped | Fall back to `Grep` for text-based search |
| `findReferences` misses some usages | Dynamic property access or string-based refs | Supplement with `Grep` for string patterns |
| Incorrect type resolution | Stale or conflicting `tsconfig.json` | Check `tsconfig.json` for correct `include`/`exclude` and `paths` |
| No LSP server available error | TypeScript not installed | Run `npm install --save-dev typescript` (see Prerequisites) |
| Slow responses on large projects | Large `node_modules` or no `tsconfig` exclude | Add `node_modules` to `exclude` in `tsconfig.json` |
| `.js` files not getting intelligence | `checkJs` not enabled | Add `"checkJs": true` to `tsconfig.json` or use JSDoc annotations |

## Best Practices

1. **Install dependencies first** — Run `npm install` so tsserver can resolve all imports and type definitions.
2. **Ensure `tsconfig.json` is correct** — It's the source of truth for tsserver's understanding of your project.
3. **Combine tools** — Use LSP for type-aware navigation, Grep for text patterns, Glob for file discovery.
4. **Check diagnostics** — LSP diagnostics reveal type errors and import issues before you even build.
5. **Use `documentSymbol` as entry point** — It gives you the map of a file without needing exact positions.
6. **Absolute paths** — Always use absolute file paths for reliable results.
7. **Works for JS too** — tsserver provides intelligence for `.js` files, especially with JSDoc or `allowJs`/`checkJs` in tsconfig.

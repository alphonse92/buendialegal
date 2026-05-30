---
name: ios-translation
description: Use when adding a new locale to an iOS Localizable.xcstrings file with batch translation, plural key handling, JSON validation, and coverage verification
---

# iOS Translation Workflow

## Overview

This skill codifies the complete process for translating all keys in an iOS `Localizable.xcstrings` JSON string catalog to a new locale. The workflow handles 287-288 localization keys, including 6 that require plural form structures (`variations.plural.{one,other}`).

Core principle: **Batch-driven translation with structural validation at every stage.**

---

## Arguments

When invoking this skill, provide:

| Argument | Required | Description |
|----------|----------|-------------|
| `language` | ✅ Yes | BCP-47 locale code (e.g., `fr`, `de`, `pt-BR`, `tr`) |
| `xcstrings_path` | ❌ No | Path to `Localizable.xcstrings`. Auto-located if omitted |

**Path resolution (when `xcstrings_path` is not provided):**
1. Run `find . -name "*.xcstrings" -type f` to locate all xcstrings files
2. **Exactly one result** → Use it; inform the user which path was selected
3. **Zero results** → Ask the user to provide the path explicitly
4. **Multiple results** → List all and ask the user to select one before proceeding

This resolution must complete before translation batching begins.

---

## The Complete Process

### Phase 1: Inventory and Planning

**Goal:** Understand scope and identify structural requirements before translation starts.

**Steps:**
1. **Enumerate all keys** — Load the xcstrings file and extract all keys from the `strings` object. Count total.
   - Expected: 287–288 keys (287 unique + 1 empty key `""`)
2. **Identify plural keys** — Discover which keys require special `variations.plural` structure by running the extraction script:
   ```bash
   python3 ./skills/ios-translation/scripts/extract_plural_keys.py [xcstrings-path]
   ```
   - Output: One key per line that uses `variations.plural` form
   - Example output shows which keys need `{"one": "...", "other": "..."}` format in patches
   - Save this list for reference during batch translation
3. **Determine batch size** — Group keys into batches of approximately 30 keys each
   - Rationale: Balances translation quality with context window efficiency
   - Total batches: ~10 batches for 287 keys
4. **Establish tone guidelines** — Document the voice and formality level for the target locale

### Phase 2: Batch Translation

**Goal:** Produce accurate JSON patches with proper structure.

**For each batch of ~30 keys:**

1. **Translate all keys in the batch**
   - Format: `{"key.name": "translated value"}`
   - For plural keys: `{"key.name": {"one": "singular", "other": "plural"}}`
   - Respect tone guidelines for the locale

2. **Handle the empty key**
   - Include it as `{"": ""}`
   - Required for consistency with EN key count

3. **Create the JSON patch**
   - Valid JSON object with translated keys and values
   - Example:
     ```json
     {
       "common.ok": "D'accord",
       "calendar.daysSelected": {"one": "Jour sélectionné: %lld", "other": "Jours sélectionnés: %lld"},
       "": ""
     }
     ```

4. **Apply the patch to xcstrings**
   - Pipe the JSON patch to the updater script:
     ```bash
     cat patch.json | python3 ./skills/ios-translation/scripts/update_xcstrings.py <lang> [path]
     ```
   - Script will warn on unknown keys or invalid formats; continue processing valid entries

### Phase 3: Structural Verification

**Goal:** Ensure xcstrings maintains valid JSON and correct pluralization structure.

**After each batch (or after all batches):**

1. **Validate JSON syntax**
   ```bash
   python3 -c "import json; json.load(open('path/to/Localizable.xcstrings')); print('✅ Valid JSON')"
   ```
   - If invalid, stop; investigate the last patch applied

2. **Verify language coverage**
   ```bash
   python3 -c "
   import json
   data = json.load(open('path/to/Localizable.xcstrings'))
   langs = {}
   for k, e in data['strings'].items():
       for l in e.get('localizations', {}): langs[l] = langs.get(l, 0) + 1
   [print(f'{l}: {c} keys') for l, c in sorted(langs.items())]
   "
   ```
   - Expected: New locale should have 288 keys (matching EN count)
   - If short: identify missing keys and re-apply in a follow-up batch

3. **Spot-check plural structures**
   ```bash
   # First, extract the plural keys for this xcstrings file
   python3 ./skills/ios-translation/scripts/extract_plural_keys.py path/to/Localizable.xcstrings > /tmp/plural_keys.txt 2>/dev/null
   
   # Then verify they have proper structure for the target language
   python3 -c "
   import json
   lang = '<your-lang-code>'
   data = json.load(open('path/to/Localizable.xcstrings'))
   
   with open('/tmp/plural_keys.txt', 'r') as f:
       plurals = [line.strip() for line in f if line.strip()]
   
   for k in plurals:
       loc = data['strings'][k]['localizations'].get(lang, {})
       has_plural = 'variations' in loc and 'plural' in loc['variations'] and 'one' in loc['variations']['plural'] and 'other' in loc['variations']['plural']
       print(f'{'✅' if has_plural else '❌'} {k}')
   "
   ```
   - All plural keys should show ✅; any ❌ indicates incorrect structure

---

## JSON Patch Format Reference

### Simple String Keys

**Format:**
```json
{"key.name": "translated text"}
```

**Resulting xcstrings structure:**
```json
"localizations": {
  "fr": {
    "stringUnit": {
      "state": "translated",
      "value": "translated text"
    }
  }
}
```

### Plural Keys

**Format:**
```json
{"calendar.daysSelected": {"one": "1 jour", "other": "%lld jours"}}
```

**Resulting xcstrings structure:**
```json
"localizations": {
  "fr": {
    "variations": {
      "plural": {
        "one": {
          "stringUnit": {
            "state": "translated",
            "value": "1 jour"
          }
        },
        "other": {
          "stringUnit": {
            "state": "translated",
            "value": "%lld jours"
          }
        }
      }
    }
  }
}
```

### Empty Key

**Format:**
```json
{"": ""}
```

**Note:** Must be included to maintain key count parity with EN.

---

## Locale Tone Guidelines

Apply these conventions to ensure consistency across translations:

| Locale | Pronoun | Formality | Key Traits |
|--------|---------|-----------|-----------|
| **es** (Spain) | tú | Informal | Warm, direct, conversational |
| **es-419** (LATAM) | vos/tú | Informal | Regional variants, friendly tone |
| **fr** | tu | Informal | Conversational, approachable |
| **pt-BR** | você | Informal | Empathetic, encouraging, warm |
| **pt-PT** | você | Semi-formal | Slightly more formal than pt-BR |
| **it** | tu | Informal | Natural, warm Italian phrasing |
| **de** | du | Informal | Friendly, direct, accessible |
| **nl** | je | Casual | Direct, straightforward, casual |
| **sv** | du | Informal | Clean, friendly, Scandinavian tone |
| **tr** | sen | Informal | Warm, approachable, informal |
| **pl** | ty | Informal | Friendly, warm, conversational |

**Error message patterns (by locale):**
- **pt-BR:** "Ops, algo deu errado" (empathetic, colloquial)
- **it:** "Qualcosa è andato storto" (natural Italian)
- **de:** "Etwas ist schief gelaufen" (friendly German)
- **tr:** "Bir hata oluştu" (warm Turkish)

---

## Updater Script Usage

**Location:** `./skills/ios-translation/scripts/update_xcstrings.py`

**Interface:**
```
python3 update_xcstrings.py <lang-code> [xcstrings-path] < patch.json
```

**Behavior:**
- Reads JSON patch from stdin
- Applies to xcstrings for the specified language
- Warns on unknown keys (does not fail)
- Warns on invalid formats for plural keys (does not fail)
- Prints count of successfully updated keys
- Writes file with `indent=2, ensure_ascii=False` (preserves Unicode, readable diffs)

**Exit codes:**
- `0` — Success
- `1` — Invalid JSON, missing file, or other error

**Example invocation:**
```bash
echo '{"common.ok": "Está bien"}' | python3 scripts/update_xcstrings.py es path/to/Localizable.xcstrings
```

---

## Common Mistakes and Fixes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| Plural key with string value | Script warns; key not updated | Supply `{"one": "...", "other": "..."}` format |
| String key with dict value | Script warns; key not updated | Supply plain string value only |
| Missing empty `""` key | Coverage count is 287 instead of 288 | Add `{"": ""}` to final patch |
| No JSON validation | Silent corruption in xcstrings | Run validation command after each batch |
| Plural key missing `%lld` placeholder | Plural counts don't show numbers | Ensure format strings are preserved: `%lld` |
| Invalid JSON in patch | Patch rejected, no keys updated | Validate JSON before piping to script |
| Wrong path provided | File not found error | Use path resolution logic or explicit path |

---

## Real-World Impact

**Verified through deployment:**
- Single updater script replaced 11+ per-language scripts (ES, ES-419, FR, PT-BR, PT-PT, IT, DE, NL, SV, TR, PL)
- Batch processing: 287 keys → ~10 batches of 30 keys each
- Validation: 100% of keys translated, plural structures verified, JSON integrity maintained
- Time per new locale: ~2–3 hours (batching, translation, validation)

---

## Verification Checklist

Before declaring a locale complete:

- [ ] JSON validation passes
- [ ] Coverage count = 288 keys
- [ ] All 6 plural keys have `variations.plural.{one,other}`
- [ ] Empty `""` key present
- [ ] No warnings from updater script for that language
- [ ] Locale code follows BCP-47 (e.g., `de` or `pt-BR`, not `pt_br`)

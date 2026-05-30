#!/usr/bin/env python3
"""
Extract plural keys from Localizable.xcstrings.

Analyzes the xcstrings JSON structure to identify keys that use variations.plural,
making the translation workflow generalistic and independent of hardcoded key lists.

Usage:
    python3 extract_plural_keys.py [xcstrings-path]
    python3 extract_plural_keys.py path/to/Localizable.xcstrings

Output: JSON array of plural key names, one per line, or pretty-printed JSON
"""
import json
import sys
from pathlib import Path


def extract_plural_keys(xcstrings_path, output_format="lines"):
    """
    Extract keys that use variations.plural structure from xcstrings.

    Args:
        xcstrings_path: Path to Localizable.xcstrings file
        output_format: "lines" (one key per line) or "json" (JSON array)

    Returns:
        List of plural key names
    """
    with open(xcstrings_path) as f:
        data = json.load(f)

    plural_keys = []

    for key, entry in data.get("strings", {}).items():
        # Check if any localization uses variations.plural structure
        localizations = entry.get("localizations", {})

        for lang, loc_data in localizations.items():
            # If this localization has variations.plural, it's a plural key
            if "variations" in loc_data and "plural" in loc_data["variations"]:
                if key not in plural_keys:
                    plural_keys.append(key)
                break  # Found it, move to next key

    return sorted(plural_keys)


def main():
    # Default xcstrings path
    if len(sys.argv) > 1:
        xcstrings_path = Path(sys.argv[1])
    else:
        xcstrings_path = Path("mobile/ios/project/app/resources/Localizable.xcstrings")

    # Validate path exists
    if not xcstrings_path.exists():
        print(f"❌ File not found: {xcstrings_path}", file=sys.stderr)
        sys.exit(1)

    try:
        plural_keys = extract_plural_keys(xcstrings_path, output_format="lines")

        if not plural_keys:
            print("⚠️  No plural keys found in xcstrings", file=sys.stderr)
            sys.exit(0)

        # Output: one key per line
        for key in plural_keys:
            print(key)

        # Also print count to stderr for visibility
        print(f"✅ Found {len(plural_keys)} plural keys", file=sys.stderr)

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

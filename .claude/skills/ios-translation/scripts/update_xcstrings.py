#!/usr/bin/env python3
"""
Generic xcstrings updater for iOS localization.

Applies JSON patches to Localizable.xcstrings for any language.
Automatically detects plural keys from the xcstrings structure.
Handles both simple strings and plural forms (variations.plural).

Usage:
    echo '{"key": "value"}' | python3 update_xcstrings.py <lang-code> [xcstrings-path]

    Examples:
        echo '{"common.ok": "D\'accord"}' | python3 update_xcstrings.py fr
        echo '{"calendar.daysSelected": {"one": "1 día", "other": "%lld días"}}' | python3 update_xcstrings.py es
"""
import json
import sys
from pathlib import Path


def extract_plural_keys(data):
    """
    Extract keys that use variations.plural from the xcstrings data.

    Args:
        data: Loaded xcstrings JSON

    Returns:
        Set of plural key names
    """
    plural_keys = set()

    for key, entry in data.get("strings", {}).items():
        localizations = entry.get("localizations", {})

        # Check if any localization uses variations.plural structure
        for lang, loc_data in localizations.items():
            if "variations" in loc_data and "plural" in loc_data["variations"]:
                plural_keys.add(key)
                break

    return plural_keys


def update_xcstrings(lang, patch, xcstrings_path):
    """Apply translation patch to xcstrings file for given language."""

    # Load the xcstrings file
    with open(xcstrings_path) as f:
        data = json.load(f)

    # Dynamically extract plural keys from the xcstrings structure
    plural_keys = extract_plural_keys(data)

    updated_count = 0

    # Apply each key-value pair from the patch
    for key, value in patch.items():
        if key not in data["strings"]:
            print(f"⚠️  Key '{key}' not found in xcstrings", file=sys.stderr)
            continue

        # Ensure localizations dict exists for this language
        if "localizations" not in data["strings"][key]:
            data["strings"][key]["localizations"] = {}

        # Handle plural keys
        if key in plural_keys:
            if isinstance(value, dict) and "one" in value and "other" in value:
                data["strings"][key]["localizations"][lang] = {
                    "variations": {
                        "plural": {
                            "one": {
                                "stringUnit": {
                                    "state": "translated",
                                    "value": value["one"]
                                }
                            },
                            "other": {
                                "stringUnit": {
                                    "state": "translated",
                                    "value": value["other"]
                                }
                            }
                        }
                    }
                }
                updated_count += 1
            else:
                print(
                    f"⚠️  Plural key '{key}' requires {{'one': '...', 'other': '...'}} format",
                    file=sys.stderr
                )
                continue
        # Handle simple string keys
        else:
            if isinstance(value, str):
                data["strings"][key]["localizations"][lang] = {
                    "stringUnit": {
                        "state": "translated",
                        "value": value
                    }
                }
                updated_count += 1
            else:
                print(
                    f"⚠️  Non-plural key '{key}' expects a string, got {type(value).__name__}",
                    file=sys.stderr
                )
                continue

    # Write the updated xcstrings file
    with open(xcstrings_path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Updated {updated_count} keys for language '{lang}'")


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: python3 update_xcstrings.py <lang-code> [xcstrings-path]",
            file=sys.stderr
        )
        print(
            "       echo '{\"key\": \"value\"}' | python3 update_xcstrings.py fr",
            file=sys.stderr
        )
        sys.exit(1)

    lang = sys.argv[1]

    # Default xcstrings path if not provided
    if len(sys.argv) > 2:
        xcstrings_path = Path(sys.argv[2])
    else:
        xcstrings_path = Path("mobile/ios/project/app/resources/Localizable.xcstrings")

    # Validate path exists
    if not xcstrings_path.exists():
        print(f"❌ File not found: {xcstrings_path}", file=sys.stderr)
        sys.exit(1)

    try:
        patch = json.load(sys.stdin)
        update_xcstrings(lang, patch, xcstrings_path)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyError as e:
        print(f"❌ Malformed xcstrings file (missing key {e})", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

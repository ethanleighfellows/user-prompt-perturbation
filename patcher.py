#!/usr/bin/env python3
"""
Converter Patcher - Fixes import issues in converter files
Replaces pyrit.identifiers imports with compatibility shim
"""

from pathlib import Path
import re

print("="*80)
print("CONVERTER FILE PATCHER")
print("="*80)

converter_dir = Path("prompt_converter")

if not converter_dir.exists():
    print("\n❌ prompt_converter/ directory not found!")
    exit(1)

# Find all converter files
converter_files = list(converter_dir.glob("*_converter.py"))
print(f"\nFound {len(converter_files)} converter files")

# Import replacements
replacements = [
    # Replace pyrit.identifiers imports
    (
        r'from pyrit\.identifiers import (\w+)',
        r'from pyrit_compat import \1'
    ),
    # Replace pyrit.common.path imports
    (
        r'from pyrit\.common\.path import (\w+)',
        r'from pyrit_compat import \1'
    ),
    # Add pyrit_compat to existing imports if needed
    (
        r'from pyrit\.models import SeedPrompt',
        'from pyrit_compat import SeedPrompt'
    ),
]

patched_count = 0
error_count = 0

for converter_file in converter_files:
    try:
        # Read the file
        content = converter_file.read_text()
        original_content = content

        # Apply replacements
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)

        # Check if anything changed
        if content != original_content:
            # Backup original
            backup_file = converter_file.with_suffix('.py.bak')
            backup_file.write_text(original_content)

            # Write patched version
            converter_file.write_text(content)

            patched_count += 1
            print(f"  ✅ Patched: {converter_file.name}")

    except Exception as e:
        error_count += 1
        print(f"  ❌ Error patching {converter_file.name}: {e}")

print(f"\n" + "="*80)
print("PATCHING COMPLETE")
print("="*80)
print(f"\n✅ Patched {patched_count} files")
print(f"❌ Errors: {error_count}")

if patched_count > 0:
    print(f"\n📝 Backups saved as *.py.bak")
    print(f"\n🚀 Now run:")
    print(f"   python script.py --verbose")
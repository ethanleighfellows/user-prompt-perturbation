#!/usr/bin/env python3
from pathlib import Path

converter_dir = Path("prompt_converter")
sample_file = converter_dir / "base64_converter.py"

if sample_file.exists():
    print("First 30 lines of base64_converter.py:")
    print("="*80)
    lines = sample_file.read_text().split('\n')[:30]
    for i, line in enumerate(lines, 1):
        print(f"{i:3}: {line}")
else:
    print("base64_converter.py not found!")

print("\n" + "="*80)
print("Checking all converter files for import patterns...")
print("="*80)

import_patterns = {}
for f in converter_dir.glob("*_converter.py"):
    content = f.read_text()
    lines = content.split('\n')
    for line in lines[:50]:  # Check first 50 lines
        if 'from pyrit' in line or 'import pyrit' in line:
            if line not in import_patterns:
                import_patterns[line] = []
            import_patterns[line].append(f.name)

if import_patterns:
    print("\nFound these pyrit imports:")
    for pattern, files in import_patterns.items():
        print(f"\n  {pattern}")
        print(f"    Used in {len(files)} files")
else:
    print("\nNo 'from pyrit' imports found!")
    print("They might already be patched or use different syntax")
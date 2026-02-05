#!/usr/bin/env python3
from pathlib import Path
import re

print("Setting up converters...")

# Step 1: Create pyrit_compat.py
converter_dir = Path("prompt_converter")
if not converter_dir.exists():
    print("ERROR: prompt_converter/ not found")
    exit(1)

compat_content = """
try:
    from pyrit.identifiers import ConverterIdentifier
except:
    class ConverterIdentifier:
        def __init__(self, **kwargs): pass

try:
    from pyrit.common.path import CONVERTER_SEED_PROMPT_PATH
except:
    from pathlib import Path
    CONVERTER_SEED_PROMPT_PATH = Path(__file__).parent

try:
    from pyrit.models import SeedPrompt
except:
    class SeedPrompt:
        @classmethod
        def from_yaml_file(cls, path): return cls()
        def render_template_value(self, **kwargs): return kwargs.get("prompt", "")
"""

(converter_dir / "pyrit_compat.py").write_text(compat_content)
print("✅ Created pyrit_compat.py")

# Step 2: Patch converters
print("Patching converters...")
patched = 0
for f in converter_dir.glob("*_converter.py"):
    content = f.read_text()
    orig = content
    content = content.replace("from pyrit.identifiers import", "from .pyrit_compat import")
    content = content.replace("from pyrit.common.path import", "from .pyrit_compat import")
    content = content.replace("from pyrit.models import SeedPrompt", "from .pyrit_compat import SeedPrompt")
    if content != orig:
        f.write_text(content)
        patched += 1
        print(f"  ✅ {f.name}")

print(f"\n✅ Done! Patched {patched} files")
print("Run: python script.py --verbose")
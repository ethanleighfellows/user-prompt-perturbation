#!/usr/bin/env python3
"""
Patch all converter files to use pyrit_compat instead of direct pyrit imports.
Rewrites imports from pyrit.* to use pyrit_compat equivalents.
"""

import re
from pathlib import Path

# Mapping of pyrit imports to pyrit_compat replacements
IMPORT_MAPPINGS = {
    # Core converter base classes
    "from pyrit.prompt_converter.prompt_converter import PromptConverter, ConverterResult": 
        "from pyrit_compat import PromptConverter, ConverterResult",
    "from pyrit.prompt_converter.prompt_converter import ConverterResult, PromptConverter": 
        "from pyrit_compat import ConverterResult, PromptConverter",
    "from pyrit.prompt_converter.prompt_converter import PromptConverter": 
        "from pyrit_compat import PromptConverter",
    "from pyrit.prompt_converter.prompt_converter import ConverterResult": 
        "from pyrit_compat import ConverterResult",
    
    # Models and data types
    "from pyrit.models import PromptDataType, data_serializer_factory": 
        "from pyrit_compat import PromptDataType, data_serializer_factory",
    "from pyrit.models import PromptDataType": 
        "from pyrit_compat import PromptDataType",
    "from pyrit.models import PromptDataType, SeedPrompt": 
        "from pyrit_compat import PromptDataType, SeedPrompt",
    "from pyrit.models import SeedPrompt": 
        "from pyrit_compat import SeedPrompt",
    "from pyrit.models import data_serializer_factory": 
        "from pyrit_compat import data_serializer_factory",
    
    # Word-level converters
    "from pyrit.prompt_converter.word_level_converter import WordLevelConverter": 
        "from pyrit_compat import WordLevelConverter",
    "from pyrit.prompt_converter.text_selection_strategy import WordSelectionStrategy": 
        "from pyrit_compat import WordSelectionStrategy",
    
    # LLM converters
    "from pyrit.prompt_converter.llm_generic_text_converter import LLMGenericTextConverter": 
        "from pyrit_compat import LLMGenericTextConverter",
    "from pyrit.prompt_target import PromptChatTarget": 
        "from pyrit_compat import PromptChatTarget",
    
    # apply_defaults
    "from pyrit.common.apply_defaults import REQUIRED_VALUE, apply_defaults": 
        "from pyrit_compat import apply_defaults",
    "from pyrit.common.apply_defaults import apply_defaults": 
        "from pyrit_compat import apply_defaults",
    "from pyrit.common.apply_defaults import REQUIRED_VALUE": 
        "pass  # REQUIRED_VALUE not available",
}

# Multi-line import patterns to handle
MULTILINE_PATTERNS = [
    # from pyrit.models import (...)
    (
        r"from pyrit\.models import \(\s*([\s\S]*?)\)",
        lambda m: handle_multiline_models_import(m.group(1))
    ),
    # from pyrit.prompt_converter.text_selection_strategy import (...)
    (
        r"from pyrit\.prompt_converter\.text_selection_strategy import \(\s*([\s\S]*?)\)",
        lambda m: "from pyrit_compat import WordSelectionStrategy"
    ),
    # from pyrit.prompt_converter.word_level_converter import (...)
    (
        r"from pyrit\.prompt_converter\.word_level_converter import \(\s*([\s\S]*?)\)",
        lambda m: "from pyrit_compat import WordLevelConverter"
    ),
    # from pyrit.exceptions import (...)
    (
        r"from pyrit\.exceptions import \(\s*([\s\S]*?)\)",
        lambda m: "pass  # pyrit.exceptions not shimmed"
    ),
]


def handle_multiline_models_import(imports_text):
    """Handle multiline imports from pyrit.models"""
    items = [item.strip() for item in imports_text.split(',') if item.strip()]
    
    result_imports = []
    for item in items:
        # Remove any comments or aliases
        item_name = item.split(' as ')[0].split('#')[0].strip()
        if item_name in ["PromptDataType", "SeedPrompt", "data_serializer_factory", "SeedDataset"]:
            result_imports.append(item_name)
    
    if result_imports:
        return "from pyrit_compat import " + ", ".join(result_imports)
    else:
        return "pass  # pyrit.models imports not available"


def patch_file(file_path: Path) -> tuple[int, int]:
    """
    Patch a single converter file.
    Returns (replacements_made, total_imports_processed)
    """
    try:
        content = file_path.read_text()
        original_content = content
        
        # First pass: handle exact matches
        for old_import, new_import in IMPORT_MAPPINGS.items():
            if old_import in content:
                content = content.replace(old_import, new_import)
        
        # Second pass: handle multiline patterns
        for pattern, replacement in MULTILINE_PATTERNS:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        # Remove duplicate imports
        lines = content.split('\n')
        seen = set()
        deduplicated_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('from pyrit_compat import') or not stripped.startswith('from pyrit'):
                if stripped not in seen or not stripped.startswith('from pyrit_compat'):
                    deduplicated_lines.append(line)
                    if stripped.startswith('from pyrit_compat'):
                        seen.add(stripped)
            else:
                deduplicated_lines.append(line)
        
        content = '\n'.join(deduplicated_lines)
        
        # Write back if changed
        if content != original_content:
            file_path.write_text(content)
            return 1, 1
        return 0, 0
        
    except Exception as e:
        print(f"Error patching {file_path}: {e}")
        return 0, 1


def main():
    """Patch all converter files in the prompt_converter directory."""
    converter_dir = Path(__file__).parent / "prompt_converter"
    
    if not converter_dir.exists():
        print(f"Error: {converter_dir} not found")
        return
    
    converter_files = sorted(converter_dir.glob("*_converter.py"))
    print(f"Found {len(converter_files)} converter files to patch")
    print("=" * 70)
    
    patched = 0
    total = 0
    
    for file_path in converter_files:
        patched_count, total_count = patch_file(file_path)
        if patched_count > 0:
            print(f"✅ {file_path.name}")
            patched += patched_count
        total += total_count
    
    print("=" * 70)
    print(f"\nSummary:")
    print(f"  Patched files: {patched}")
    print(f"  Total processed: {total}")
    
    if patched > 0:
        print(f"\n✅ Successfully patched {patched} converter files!")
        print("All imports should now work with pyrit_compat compatibility shim.")
    else:
        print("\n⚠️  No files needed patching (or already patched)")


if __name__ == "__main__":
    main()

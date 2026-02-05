# PyRIT Prompt Converter - Batch Processing Guide

A powerful batch processing tool for applying multiple prompt converters to Excel/CSV datasets. Automatically obfuscates, encodes, and transforms text prompts using 23+ converters.

---

## Table of Contents
- [Setup & Dependencies](#setup--dependencies)
- [Quick Start](#quick-start)
- [Usage Guide](#usage-guide)
- [Supported Converters](#supported-converters)
- [Output Format](#output-format)
- [Troubleshooting](#troubleshooting)

---

## Setup & Dependencies

### Requirements
- **Python 3.10+** (tested on 3.13)
- **PyRIT 0.10.0** (Microsoft's Python Risk Identification Tool for LLMs)
- Excel/CSV files for input

### Step 1: Install Dependencies

```bash
# Install PyRIT and required packages
pip install pyrit pandas openpyxl

# Or install all dependencies from requirements
pip install -r requirements.txt
```

### Step 2: Verify Installation

```bash
# Check PyRIT version
python3 -c "import pyrit; print(pyrit.__version__)"

# Should output: 0.10.0 (or compatible version)
```

### Step 3: Project Structure

```
Mass-Prompt-Convert/
├── script.py                    # Main processor script
├── prompt_converter/            # Local converter modules
│   ├── __init__.py
│   ├── pyrit_compat.py         # Compatibility shim for PyRIT
│   ├── base64_converter.py
│   ├── caesar_converter.py
│   └── ... (23 total converters)
├── sample_prompts.xlsx         # Example input file
└── README.md                   # This file
```

### Step 4: First-Time Setup

The script auto-initializes on first run. No additional setup needed—`pyrit_compat.py` handles compatibility layer automatically.

---

## Quick Start

### Process a Full Excel File

```bash
# Process all rows in Excel file
python3 script.py enterprise-chat-clean_labeled.xlsx

# Output: enriched_prompts_YYYYMMDD_HHMMSS.xlsx
```

### Process with Custom Output Name

```bash
python3 script.py input.xlsx -o my_output.xlsx
```

### Process Only First N Rows (for testing)

```bash
# Process only first 5 rows
python3 script.py input.xlsx -m 5
```

### Test a Single Prompt

```bash
python3 script.py -p "Your prompt here"

# Output: prompt_variations_YYYYMMDD_HHMMSS.xlsx
```

---

## Usage Guide

### Command Syntax

```bash
python3 script.py [INPUT_FILE] [OPTIONS]
```

### Options

| Option | Short | Type | Description |
|--------|-------|------|-------------|
| `--output` | `-o` | `PATH` | Custom output file path |
| `--prompt` | `-p` | `TEXT` | Process single prompt (instead of file) |
| `--prompt-column` | `-c` | `TEXT` | Column name containing prompts (default: `prompt`) |
| `--max-rows` | `-m` | `INT` | Limit rows processed (for testing) |
| `--verbose` | `-v` | FLAG | Show detailed debug information |

### Examples

#### Example 1: Full Processing
```bash
python3 script.py dataset.xlsx -o results.xlsx
```
- Reads `dataset.xlsx`
- Applies all 23 converters to each row
- Saves to `results.xlsx` with new columns

#### Example 2: Testing with Limited Rows
```bash
python3 script.py dataset.xlsx -m 10 -o test_output.xlsx
```
- Processes only first 10 rows
- Useful for validating before full run

#### Example 3: Different Column Name
```bash
python3 script.py data.xlsx -c "instruction" -o output.xlsx
```
- Reads prompts from `instruction` column (not `prompt`)

#### Example 4: Single Prompt Test
```bash
python3 script.py -p "Write a poem about cats"
```
- Tests all converters on single prompt
- Creates `prompt_variations_*.xlsx` output

#### Example 5: Verbose Debug Output
```bash
python3 script.py dataset.xlsx --verbose 2>&1 | head -100
```
- Shows why converters failed/passed
- Useful for troubleshooting

---

## Supported Converters

### 23 Working Text-to-Text Converters

| # | Converter | Transformation | Use Case |
|---|-----------|---|----------|
| 1 | **AsciiArtConverter** | Text → ASCII art | Visual obfuscation |
| 2 | **AskToDecodeConverter** | Add encoding indicators | Bypass encoding detection |
| 3 | **AtbashConverter** | Atbash cipher (reverse alphabet) | Classical cipher |
| 4 | **Base2048Converter** | Base2048 encoding | Dense binary representation |
| 5 | **Base64Converter** | Base64 encoding | Standard encoding |
| 6 | **BrailleConverter** | Convert to Braille symbols | Accessibility obfuscation |
| 7 | **CaesarConverter** | Caesar cipher (ROT13) | Classic substitution cipher |
| 8 | **CharacterSpaceConverter** | Add spaces between characters | Character-level obfuscation |
| 9 | **ColloquialWordswapConverter** | Informal language substitution | Style transformation |
| 10 | **DiacriticConverter** | Add accents/diacritics | Unicode variation |
| 11 | **EcojiConverter** | Convert to emoji | Visual encoding |
| 12 | **FlipConverter** | Reverse text | Mirror transformation |
| 13 | **HumanInTheLoopConverter** | Pass-through (batch mode) | Human review in interactive mode |
| 14 | **InsertPunctuationConverter** | Add punctuation marks | Punctuation obfuscation |
| 15 | **MathObfuscationConverter** | Express text as math equations | Mathematical encoding |
| 16 | **MorseConverter** | Convert to Morse code | Morse code representation |
| 17 | **NatoConverter** | NATO phonetic alphabet | Phonetic encoding |
| 18 | **NegationTrapConverter** | Invert meaning with negation | Semantic transformation |
| 19 | **RandomCapitalLettersConverter** | Random capitalization | Case variation |
| 20 | **TemplateSegmentConverter** | Embed in multi-entity template | Template-based obfuscation |
| 21 | **UnicodeConfusableConverter** | Homoglyph substitution | Unicode lookalikes |
| 22 | **UnicodeSubstitutionConverter** | Unicode character replacement | Zero-width characters |
| 23 | **UrlConverter** | URL encode text | URL-safe encoding |
| 24 | **ZeroWidthConverter** | Add zero-width characters | Invisible character obfuscation |

### Converter Categorization

**Encoding/Cipher:**
- Base64, Base2048, Braille, Caesar, Morse, NATO, URL, Ecoji

**Character Manipulation:**
- CharacterSpace, DiacriticConverter, RandomCapitalLetters, UnicodeConfusable, UnicodeSubstitution, ZeroWidth

**Semantic/Structure:**
- AskToDecode, Flip, InsertPunctuation, MathObfuscation, NegationTrap, TemplateSegment

**Other:**
- ColloquialWordswap, HumanInTheLoop

---

## Output Format

### Excel Output Columns

Input file:
| prompt |
|--------|
| "test" |

Output file (24 columns):
| prompt | AsciiArtConverter_output | AtbashConverter_output | Base64Converter_output | ... |
|--------|---|---|---|---|
| "test" | [ASCII art] | "gvhg" | "dGVzdA==" | ... |

### Output File Naming

**Default (auto-generated):**
```
enriched_prompts_20260205_101540.xlsx
```
Format: `enriched_prompts_YYYYMMDD_HHMMSS.xlsx`

**Custom (with -o flag):**
```bash
python3 script.py input.xlsx -o my_results.xlsx
```

---

## Processing Information

### Performance Expectations

- **Discovery Phase**: ~2-3 seconds (loads & tests all converters)
- **Per-Row Processing**: ~0.5-2 seconds (depends on converter complexity)
- **Total Time**: Roughly `discovery_time + (num_rows × 0.5-2 seconds)`

**Example:** 1000 rows
```
Discovery: 3 seconds
Processing: 1000 rows × 1 second = 1000 seconds (~17 minutes)
Total: ~17 minutes
```

### Batch Mode Features

✅ **No User Interaction Required**
- Processes entire datasets automatically
- HumanInTheLoopConverter auto-proceeds (non-interactive mode detection)
- Perfect for CI/CD pipelines and scheduled jobs

✅ **Error Handling**
- Failed converters logged but processing continues
- Errors recorded in output file cells (ERROR: reason)
- Full error details available with `--verbose` flag

✅ **Memory Efficient**
- Processes row-by-row (not entire file in memory)
- Suitable for large Excel files

---

## Troubleshooting

### Issue: "No working text-to-text converters found"

```
❌ ERROR: No working text-to-text converters found!
```

**Solution:**
1. Verify PyRIT installation: `pip show pyrit`
2. Run with verbose flag: `python3 script.py --verbose`
3. Check Python version: `python3 --version` (need 3.10+)

### Issue: "ModuleNotFoundError: No module named 'pandas'"

```bash
pip install pandas openpyxl
```

### Issue: Script hangs or takes very long

**Normal:** Some converters take 1-2 seconds per row
**Timeout:** If hangs >10 seconds, likely a converter bug
- Use `--max-rows 1` to test
- Check `--verbose` output for which converter is stuck

### Issue: Output file not created

Check:
1. Write permissions in current directory: `ls -la`
2. Disk space: `df -h`
3. Valid input file format (.xlsx or .csv)

**Fallback:** Script auto-converts to CSV if Excel write fails

### Issue: Specific converter failing

Use verbose mode to see specific errors:
```bash
python3 script.py input.xlsx --verbose 2>&1 | grep "❌"
```

---

## Advanced Usage

### Batch Process Multiple Files

```bash
# Loop through all Excel files
for file in *.xlsx; do
    python3 script.py "$file" -o "processed_$file"
done
```

### Extract Specific Converters' Output

```bash
# After running script, use pandas to extract columns
python3 << 'EOF'
import pandas as pd

df = pd.read_excel('enriched_prompts_20260205_101540.xlsx')
# Get original prompt and Base64 encoding
result = df[['prompt', 'Base64Converter_output']]
result.to_excel('base64_only.xlsx', index=False)
print("✅ Extracted Base64 columns")
EOF
```

### Monitor Progress with Logging

```bash
# Save full log of processing
python3 script.py input.xlsx 2>&1 | tee process.log
```

---

## Examples

### Example: Process Security Prompts Dataset

```bash
# Input: dataset of harmful prompts
python3 script.py red_team_prompts.xlsx -o red_team_obfuscated.xlsx

# Output: 1 + 23 = 24 columns
# Column 1: Original prompt
# Columns 2-24: Obfuscated variations
```

### Example: Create Training Dataset Variations

```bash
# Original training data
python3 script.py training_set.xlsx -o training_set_augmented.xlsx

# Result: Each prompt has 23 variations for model robustness testing
```

### Example: Test Single Prompt Before Batch

```bash
# Test what converters do to a specific prompt
python3 script.py -p "write a SQL injection payload"

# Review output in prompt_variations_*.xlsx
# Then process full dataset
python3 script.py full_dataset.xlsx
```

---

## Performance Optimization

### For Large Files (10,000+ rows)

1. **Test first with sample:**
   ```bash
   python3 script.py large_file.xlsx -m 100 -o test.xlsx
   ```

2. **Run with verbose disabled** (default):
   ```bash
   python3 script.py large_file.xlsx -o results.xlsx
   # Don't use --verbose for large runs
   ```

3. **Monitor progress:**
   ```bash
   python3 script.py large_file.xlsx 2>&1 | grep "🔄"
   ```

### Parallel Processing (Manual)

For very large files, split and process in parallel:
```bash
# Split large file into chunks
python3 << 'EOF'
import pandas as pd
df = pd.read_excel('huge_file.xlsx')
for i, chunk in enumerate(df.groupby(df.index // 5000)):
    chunk[1].to_excel(f'chunk_{i}.xlsx', index=False)
EOF

# Process in parallel (macOS/Linux)
for file in chunk_*.xlsx; do
    python3 script.py "$file" -o "result_$file" &
done
wait
```

---

## Support & Feedback

### Getting Help

1. **Check logs:** Run with `--verbose` flag
2. **Test converter:** Use `-p` flag with single prompt
3. **Verify setup:** `python3 script.py --help`

### Report Issues

Include:
- Python version: `python3 --version`
- PyRIT version: `pip show pyrit`
- Command used
- Error message (with `--verbose` output)
- Sample input file (if possible)

---

## License

Built with [PyRIT](https://github.com/Azure/PyRIT) - Microsoft's Python Risk Identification Tool for LLMs

---

**Version:** 1.0  
**Last Updated:** February 5, 2026  
**Status:** ✅ Production Ready

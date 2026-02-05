#!/usr/bin/env python3
"""
Excel Prompt Converter Processor - VERBOSE VERSION
Shows detailed failure reasons for debugging
"""

import asyncio
import logging
import sys
import importlib
import importlib.util
import inspect
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

# Pre-import pyrit_compat to make it available to all converter modules
# This is done by adding it to sys.modules so converters can do: from pyrit_compat import ...
converter_dir = Path(__file__).parent / "prompt_converter"
pyrit_compat_path = converter_dir / "pyrit_compat.py"
spec = importlib.util.spec_from_file_location("pyrit_compat", pyrit_compat_path)
pyrit_compat = importlib.util.module_from_spec(spec)
sys.modules['pyrit_compat'] = pyrit_compat
spec.loader.exec_module(pyrit_compat)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConverterDiscovery:
    """Discovers and tests all available prompt converters from local directory."""

    def __init__(self, verbose: bool = False):
        self.working_converters: Dict[str, Any] = {}
        self.failed_converters: Dict[str, str] = {}
        self.text_to_text_converters: Dict[str, Any] = {}
        self.verbose = verbose

    async def discover_and_test_converters(self):
        """Discover all converters from local prompt_converter directory."""
        logger.info("🔍 Starting converter discovery from local directory...")

        converter_dir = Path(__file__).parent / "prompt_converter"
        if not converter_dir.exists():
            logger.error(f"❌ Directory not found: {converter_dir}")
            return

        logger.info(f"📁 Found converter directory: {converter_dir}")

        converter_files = list(converter_dir.glob("*_converter.py"))
        logger.info(f"📦 Found {len(converter_files)} converter files")

        for converter_file in sorted(converter_files):
            module_name = converter_file.stem
            await self._test_converter_module(module_name)

        logger.info(f"\n✅ Working converters: {len(self.working_converters)}")
        logger.info(f"❌ Failed converters: {len(self.failed_converters)}")
        logger.info(f"🎯 Text-to-text converters: {len(self.text_to_text_converters)}")

        # Show failure details if verbose
        if self.verbose and self.failed_converters:
            print("\n" + "="*80)
            print("FAILURE DETAILS")
            print("="*80)
            for name, error in sorted(self.failed_converters.items())[:20]:
                print(f"\n❌ {name}:")
                print(f"   {error}")

    async def _test_converter_module(self, module_name: str):
        """Test a converter module from local directory."""
        try:
            module = importlib.import_module(f'prompt_converter.{module_name}')

            converter_classes = [
                (name, obj) for name, obj in inspect.getmembers(module, inspect.isclass)
                if name.endswith('Converter') and not name.startswith('_')
            ]

            if not converter_classes:
                if self.verbose:
                    logger.debug(f"  ⚠️  {module_name}: No converter classes found")
                return

            for class_name, converter_class in converter_classes:
                await self._test_converter_class(class_name, converter_class)

        except Exception as e:
            error_msg = f"Import failed: {type(e).__name__}: {str(e)}"
            if self.verbose:
                logger.debug(f"  ❌ {module_name}: {error_msg}")
            self.failed_converters[module_name] = error_msg

    async def _test_converter_class(self, class_name: str, converter_class: Any):
        """Test if a converter class can be instantiated and used."""
        try:
            # Try to instantiate with various parameter combinations
            converter_instance = await self._try_instantiate(converter_class, class_name)

            if converter_instance is None:
                self.failed_converters[class_name] = "Could not instantiate with any known parameters"
                return

            supported_inputs = getattr(converter_instance, 'SUPPORTED_INPUT_TYPES', ())
            supported_outputs = getattr(converter_instance, 'SUPPORTED_OUTPUT_TYPES', ())

            is_text_to_text = 'text' in supported_inputs and 'text' in supported_outputs

            # Test conversion (with timeout to avoid hanging on interactive converters)
            try:
                # Skip HumanInTheLoopConverter testing as it requires user interaction
                if class_name == "HumanInTheLoopConverter":
                    # Just mark it as working without testing
                    self.working_converters[class_name] = {
                        'instance': converter_instance,
                        'inputs': supported_inputs,
                        'outputs': supported_outputs,
                        'is_text_to_text': is_text_to_text
                    }
                    if is_text_to_text:
                        self.text_to_text_converters[class_name] = converter_instance
                        logger.info(f"  ✅ {class_name} - Text→Text (skipped test)")
                else:
                    test_result = await asyncio.wait_for(
                        converter_instance.convert_async(
                            prompt="test",
                            input_type="text"
                        ),
                        timeout=5.0  # 5 second timeout
                    )

                    self.working_converters[class_name] = {
                        'instance': converter_instance,
                        'inputs': supported_inputs,
                        'outputs': supported_outputs,
                        'is_text_to_text': is_text_to_text
                    }

                    if is_text_to_text:
                        self.text_to_text_converters[class_name] = converter_instance
                        logger.info(f"  ✅ {class_name} - Text→Text")
                    else:
                        input_type = supported_inputs[0] if supported_inputs else 'unknown'
                        output_type = supported_outputs[0] if supported_outputs else 'unknown'
                        logger.info(f"  ⚠️  {class_name} - {input_type}→{output_type}")

            except asyncio.TimeoutError:
                error_msg = f"Conversion test timeout (likely interactive converter)"
                self.failed_converters[class_name] = error_msg
                if self.verbose:
                    logger.debug(f"  ⏱️  {class_name} - {error_msg}")

        except Exception as e:
            error_msg = f"Testing failed: {type(e).__name__}: {str(e)}"
            self.failed_converters[class_name] = error_msg
            if self.verbose:
                logger.debug(f"  ❌ {class_name} - {error_msg}")

    async def _try_instantiate(self, converter_class: Any, class_name: str) -> Any:
        """Try to instantiate a converter with many parameter patterns."""

        # Expanded list of instantiation patterns
        patterns = [
            {},  # No parameters
            {'append_description': False},
            {'caesar_offset': 13},
            {'caesar_offset': 13, 'append_description': False},
            {'font': 'block'},
            {'font': 'rand'},
            {'encoding_func': 'b64encode'},
            {'encoding_name': 'cipher'},
            {'bits_per_char': 8},
            {'shift_value': 0},
            {'template': None},
            {'output_format': 'wav'},
            {'synthesis_language': 'en-US'},
            {'recognition_language': 'en-US'},
            {'img_to_add': ''},
            {'video_path': ''},
            {'text_to_add': 'test'},
            # Word-level converter patterns
            {'word_selection_strategy': None},
            {'word_split_separator': ' '},
            # LLM converter patterns (will fail but try anyway)
            {'converter_target': None},
            {'prompt_target': None},
        ]

        # Try each pattern
        for params in patterns:
            try:
                instance = converter_class(**params)
                if self.verbose:
                    logger.debug(f"    ✅ {class_name} instantiated with: {params}")
                return instance
            except TypeError as e:
                # Wrong parameters, continue
                continue
            except ValueError as e:
                # Invalid parameter value
                error_str = str(e).lower()
                if 'required' in error_str or 'empty' in error_str or 'valid' in error_str:
                    # These are parameter validation errors, continue
                    continue
                else:
                    # Real error, stop
                    if self.verbose:
                        logger.debug(f"    ❌ {class_name} ValueError: {e}")
                    break
            except Exception as e:
                # Other error, stop trying
                error_str = str(e).lower()
                if "required" not in error_str and "missing" not in error_str:
                    if self.verbose:
                        logger.debug(f"    ❌ {class_name} {type(e).__name__}: {e}")
                    break

        return None


class ExcelPromptProcessor:
    """Processes Excel workbook with prompt converters."""

    def __init__(self, discovery: ConverterDiscovery):
        self.discovery = discovery

    async def process_excel(
        self,
        input_file: str,
        output_file: Optional[str] = None,
        prompt_column: str = 'prompt',
        max_rows: Optional[int] = None
    ):
        """Process Excel file by running all working converters on each prompt."""
        logger.info(f"\n📊 Processing Excel file: {input_file}")

        try:
            df = pd.read_excel(input_file)
        except Exception:
            try:
                df = pd.read_csv(input_file)
            except Exception as e:
                logger.error(f"Failed to read input file: {e}")
                return

        if prompt_column not in df.columns:
            logger.error(f"Column '{prompt_column}' not found. Available: {list(df.columns)}")
            return

        if max_rows:
            df = df.head(max_rows)

        logger.info(f"📝 Processing {len(df)} rows with {len(self.discovery.text_to_text_converters)} converters")

        results = df.copy()

        for idx in range(len(df)):
            prompt = df.iloc[idx][prompt_column]

            if pd.isna(prompt) or str(prompt).strip() == '':
                continue

            logger.info(f"\n🔄 Processing row {idx + 1}/{len(df)}: {str(prompt)[:50]}...")

            for converter_name, converter in self.discovery.text_to_text_converters.items():
                try:
                    result = await converter.convert_async(
                        prompt=str(prompt),
                        input_type="text"
                    )

                    column_name = f"{converter_name}_output"
                    results.loc[idx, column_name] = result.output_text

                    logger.debug(f"  ✅ {converter_name}: {result.output_text[:30]}...")

                except Exception as e:
                    logger.warning(f"  ⚠️  {converter_name} failed: {e}")
                    column_name = f"{converter_name}_output"
                    results.loc[idx, column_name] = f"ERROR: {str(e)}"

        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"enriched_prompts_{timestamp}.xlsx"

        try:
            results.to_excel(output_file, index=False)
            logger.info(f"\n💾 Saved enriched data to: {output_file}")
            logger.info(f"📈 Original columns: {len(df.columns)} → New columns: {len(results.columns)}")
        except Exception as e:
            csv_file = output_file.replace('.xlsx', '.csv')
            results.to_csv(csv_file, index=False)
            logger.info(f"\n💾 Saved enriched data to CSV: {csv_file}")

    async def process_single_prompt(self, prompt: str) -> pd.DataFrame:
        """Process a single prompt with all working converters."""
        logger.info(f"\n🎯 Processing prompt: {prompt}")

        results = {
            'Converter': [],
            'Input': [],
            'Output': [],
            'Status': []
        }

        for converter_name, converter in self.discovery.text_to_text_converters.items():
            try:
                result = await converter.convert_async(
                    prompt=prompt,
                    input_type="text"
                )

                results['Converter'].append(converter_name)
                results['Input'].append(prompt)
                results['Output'].append(result.output_text)
                results['Status'].append('✅ Success')

                logger.info(f"  ✅ {converter_name}")

            except Exception as e:
                results['Converter'].append(converter_name)
                results['Input'].append(prompt)
                results['Output'].append(str(e))
                results['Status'].append(f'❌ {type(e).__name__}')

                logger.warning(f"  ❌ {converter_name}: {e}")

        return pd.DataFrame(results)


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Excel Prompt Converter Processor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument('input_file', nargs='?', help='Input Excel/CSV file')
    parser.add_argument('-o', '--output', help='Output file path')
    parser.add_argument('-p', '--prompt', help='Single prompt to process')
    parser.add_argument('-c', '--prompt-column', default='prompt', help='Prompt column name')
    parser.add_argument('-m', '--max-rows', type=int, help='Max rows to process')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output (show why converters fail)')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    discovery = ConverterDiscovery(verbose=args.verbose)
    await discovery.discover_and_test_converters()

    if len(discovery.text_to_text_converters) == 0:
        print("\n❌ ERROR: No working text-to-text converters found!")
        print("\nRun with --verbose to see why converters are failing:")
        print("  python script.py --verbose")
        sys.exit(1)

    processor = ExcelPromptProcessor(discovery)

    if args.prompt:
        results_df = await processor.process_single_prompt(args.prompt)
        output_file = args.output or f"prompt_variations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        try:
            results_df.to_excel(output_file, index=False)
        except:
            output_file = output_file.replace('.xlsx', '.csv')
            results_df.to_csv(output_file, index=False)

        print("\n" + "="*80)
        print("RESULTS SUMMARY")
        print("="*80)
        print(results_df.to_string(index=False))
        print(f"\n💾 Saved to: {output_file}")

    elif args.input_file:
        await processor.process_excel(
            input_file=args.input_file,
            output_file=args.output,
            prompt_column=args.prompt_column,
            max_rows=args.max_rows
        )
    else:
        parser.print_help()
        sys.exit(1)

    print("\n" + "="*80)
    print("CONVERTER SUMMARY")
    print("="*80)
    print(f"✅ Working text-to-text converters: {len(discovery.text_to_text_converters)}")
    print(f"⚠️  Other converters (image/audio/etc): {len(discovery.working_converters) - len(discovery.text_to_text_converters)}")
    print(f"❌ Failed converters: {len(discovery.failed_converters)}")

    if discovery.text_to_text_converters:
        print("\nWorking Text-to-Text Converters:")
        for name in sorted(discovery.text_to_text_converters.keys()):
            print(f"  • {name}")


if __name__ == "__main__":
    asyncio.run(main())

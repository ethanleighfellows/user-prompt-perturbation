# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import logging
import pathlib
from typing import Optional

from pyrit_compat import apply_defaults
from pyrit_compat import CONVERTER_SEED_PROMPT_PATH
from pyrit_compat import ConverterIdentifier
from pyrit_compat import SeedPrompt
from pyrit_compat import LLMGenericTextConverter
from pyrit_compat import PromptChatTarget

logger = logging.getLogger(__name__)


class ToneConverter(LLMGenericTextConverter):
    """
    Converts a conversation to a different tone using an LLM.

    An existing ``PromptChatTarget`` is used to perform the conversion (like Azure OpenAI).
    """

    @apply_defaults
    def __init__(
        self,
        *,
        converter_target: PromptChatTarget = REQUIRED_VALUE,  # type: ignore[assignment]
        tone: str,
        prompt_template: Optional[SeedPrompt] = None,
    ):
        """
        Initialize the converter with the target chat support, tone, and optional prompt template.

        Args:
            converter_target (PromptChatTarget): The target chat support for the conversion which will translate.
                Can be omitted if a default has been configured via PyRIT initialization.
            tone (str): The tone for the conversation. E.g. upset, sarcastic, indifferent, etc.
            prompt_template (SeedPrompt, Optional): The prompt template for the conversion.

        Raises:
            ValueError: If the language is not provided.
        """
        # set to default strategy if not provided
        prompt_template = (
            prompt_template
            if prompt_template
            else SeedPrompt.from_yaml_file(pathlib.Path(CONVERTER_SEED_PROMPT_PATH) / "tone_converter.yaml")
        )

        super().__init__(
            converter_target=converter_target,
            system_prompt_template=prompt_template,
            tone=tone,
        )
        self._tone = tone

    def _build_identifier(self) -> ConverterIdentifier:
        """
        Build the converter identifier with tone parameters.

        Returns:
            ConverterIdentifier: The identifier for this converter.
        """
        return self._create_identifier(
            converter_target=self._converter_target,
            converter_specific_params={
                "tone": self._tone,
            },
        )

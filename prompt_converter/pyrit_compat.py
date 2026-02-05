"""
PyRIT Compatibility Shim
Provides dummy implementations of PyRIT classes that may be missing or incompatible.
This allows converters built for different PyRIT versions to run locally.
"""

from typing import Optional, Any, Dict, Literal, TypeVar, Generic
from pathlib import Path
import uuid

T = TypeVar('T')


# ============================================================================
# CORE COMPATIBILITY IMPORTS - Try real PyRIT first, fall back to shims
# ============================================================================

# ConverterIdentifier - Used by all converters
try:
    from pyrit.identifiers import ConverterIdentifier
except ImportError:
    class ConverterIdentifier:
        """Dummy ConverterIdentifier for converters."""
        def __init__(self, **kwargs):
            self.id = str(uuid.uuid4())
            self.type_name = kwargs.get('type_name', 'unknown')


# CONVERTER_SEED_PROMPT_PATH - Used by seed/template converters
try:
    from pyrit.common.path import CONVERTER_SEED_PROMPT_PATH
except ImportError:
    CONVERTER_SEED_PROMPT_PATH = Path(__file__).parent / "seeds"


# DB_DATA_PATH - Used by converters needing data storage
try:
    from pyrit.common.path import DB_DATA_PATH
except ImportError:
    DB_DATA_PATH = Path(__file__).parent / "db_data"


# DATASETS_PATH - Used by dataset-dependent converters
try:
    from pyrit.common.path import DATASETS_PATH
except ImportError:
    DATASETS_PATH = Path(__file__).parent / "datasets"


# SeedPrompt - Used by converters with seed templates
try:
    from pyrit.models import SeedPrompt
except ImportError:
    class SeedPrompt:
        """Dummy SeedPrompt for template-based converters."""
        def __init__(self, name: str = "", data: str = ""):
            self.name = name
            self.data = data
            self.template = data
        
        @classmethod
        def from_yaml_file(cls, path):
            """Load seed prompt from YAML file."""
            return cls(name=Path(path).stem)
        
        def render_template_value(self, **kwargs):
            """Render template with given values."""
            return kwargs.get("prompt", "") or self.data


# Identifiable - Base class for identifiable objects
class Identifiable(Generic[T]):
    """Generic identifiable base class that can hold any identifier type."""
    def __init__(self):
        self.id = str(uuid.uuid4())


# ============================================================================
# CORE CONVERTER CLASSES - Essential for all converters to work
# ============================================================================

class ConverterResult:
    """Result of a converter operation."""
    def __init__(self, output_text: str, output_type: str = "text"):
        self.output_text = output_text
        self.output_type = output_type


class PromptDataType:
    """Enum-like class for prompt data types."""
    text = "text"
    image = "image"
    audio = "audio"
    video = "video"
    
    @staticmethod
    def is_valid(data_type):
        return data_type in ("text", "image", "audio", "video")


class PromptConverter:
    """
    Base class for prompt converters.
    All converters should inherit from this.
    """
    
    SUPPORTED_INPUT_TYPES: tuple = ("text",)
    SUPPORTED_OUTPUT_TYPES: tuple = ("text",)
    
    def __init__(self, **kwargs):
        """Initialize converter with optional parameters."""
        self.params = kwargs
    
    def input_supported(self, input_type: str) -> bool:
        """Check if input type is supported."""
        return input_type in self.SUPPORTED_INPUT_TYPES
    
    def output_supported(self, output_type: str) -> bool:
        """Check if output type is supported."""
        return output_type in self.SUPPORTED_OUTPUT_TYPES
    
    async def convert_async(self, *, prompt: str, input_type: str = "text") -> ConverterResult:
        """
        Convert prompt asynchronously.
        Subclasses should override this method.
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement convert_async()")
    
    def convert(self, *, prompt: str, input_type: str = "text") -> ConverterResult:
        """
        Convert prompt synchronously.
        Subclasses can override this for sync support.
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement convert() or convert_async()")
    
    def _build_identifier(self):
        """Build converter identifier. Override in subclasses."""
        return ConverterIdentifier()


# ============================================================================
# OPTIONAL CONVERTER TYPES - For specialized converters
# ============================================================================

class WordLevelConverter(PromptConverter):
    """Base class for word-level text converters."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.word_selection_strategy = kwargs.get('word_selection_strategy', None)
        self.word_split_separator = kwargs.get('word_split_separator', ' ')


class WordSelectionStrategy:
    """Strategy for selecting words in text."""
    
    FIRST = "first"
    LAST = "last"
    RANDOM = "random"
    ALL = "all"


class PromptChatTarget:
    """Base class for prompt targets (LLM endpoints)."""
    
    def __init__(self, **kwargs):
        self.config = kwargs


# ============================================================================
# LLM-RELATED CLASSES - For LLM-based converters
# ============================================================================

class LLMResponse:
    """Response from an LLM."""
    def __init__(self, content: str):
        self.content = content


class LLMGenericTextConverter(PromptConverter):
    """
    Base class for LLM-based text converters.
    Uses an LLM to transform text according to a template.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.converter_target = kwargs.get('converter_target', None)
        self.template = kwargs.get('template', None)


# ============================================================================
# DATA/FILE HANDLING - For converters that process files
# ============================================================================

def data_serializer_factory(data_type: str):
    """Factory for creating data serializers."""
    class DummySerializer:
        @staticmethod
        def serialize(data):
            return str(data)
        
        @staticmethod
        def deserialize(data):
            return data
    
    return DummySerializer()


def apply_defaults(**kwargs):
    """Decorator to apply default values to function arguments."""
    def decorator(func):
        async def wrapper(*args, **call_kwargs):
            merged = {**kwargs, **call_kwargs}
            return await func(*args, **merged)
        return wrapper
    return decorator


# ============================================================================
# AUTHENTICATION - For converters that need credentials
# ============================================================================

class AzureAuth:
    """Dummy Azure authentication."""
    def __init__(self, **kwargs):
        self.credentials = kwargs


# ============================================================================
# EXCEPTION CLASSES - For error handling
# ============================================================================

class ConverterException(Exception):
    """Base exception for converter errors."""
    pass


class InvalidInputException(ConverterException):
    """Invalid input exception."""
    pass


class ConversionException(ConverterException):
    """Conversion failed exception."""
    pass


# ============================================================================
# EXPOSURE - Export all compatibility classes
# ============================================================================

__all__ = [
    # Core compatibility
    "ConverterIdentifier",
    "Identifiable",
    "CONVERTER_SEED_PROMPT_PATH",
    "DB_DATA_PATH",
    "DATASETS_PATH",
    "SeedPrompt",
    # Core converter classes
    "ConverterResult",
    "PromptDataType",
    "PromptConverter",
    # Optional converter types
    "WordLevelConverter",
    "WordSelectionStrategy",
    "PromptChatTarget",
    # LLM-related
    "LLMResponse",
    "LLMGenericTextConverter",
    # Data/file handling
    "data_serializer_factory",
    "apply_defaults",
    # Authentication
    "AzureAuth",
    # Exceptions
    "ConverterException",
    "InvalidInputException",
    "ConversionException",
]

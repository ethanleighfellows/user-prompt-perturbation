"""
Prompt Converter Package
Local collection of prompt converters
"""

# Make pyrit_compat available globally by adding to sys.modules
import sys
from . import pyrit_compat

# This allows converters to do: from pyrit_compat import ...
sys.modules['pyrit_compat'] = pyrit_compat

__version__ = "1.0.0"
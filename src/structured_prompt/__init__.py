"""
Structured Prompt Framework

A framework for creating extensible, reusable, and standardized prompts
that can be easily modified by LLMs and adapted across organizations.
"""

from __future__ import annotations

# Import builder components
from .builder import (
    IndentationPreferences,
    Item,
    ItemLike,
    PromptSection,
    PromptText,
    StructuredPromptFactory,
)

# Import generator
from .generator import PromptStructureGenerator

__version__ = "0.1.0"

__all__ = [
    # Builder classes
    "IndentationPreferences",
    "Item",
    "ItemLike",
    "PromptSection",
    "PromptText",
    "StructuredPromptFactory",
    # Generator
    "PromptStructureGenerator",
    # Version
    "__version__",
]

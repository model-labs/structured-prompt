from __future__ import annotations

# Thin compatibility shim: re-export public API from the structured builder package
from .builder import (
    IndentationPreferences,
    Item,
    PromptText,
    PromptSection,
    StructuredPromptFactory,
    ItemLike,
)

__all__ = [
    "IndentationPreferences",
    "Item",
    "PromptText",
    "PromptSection",
    "StructuredPromptFactory",
    "ItemLike",
]

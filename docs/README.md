# Structured Prompt Framework Documentation

This directory contains comprehensive documentation for using the Structured Prompt Framework.

## Documentation Files

### [Usage Patterns Guide](usage-patterns.md)
**Comprehensive guide covering all major usage patterns and syntaxes**

- Complete API overview with examples
- Stage definition and generation workflows
- Content assignment semantics (append vs replace)
- Hierarchical stage addressing
- Formatting and styling options
- Critical steps and mandatory actions
- Advanced usage patterns
- CLI usage
- Real-world complete examples

**Best for:** Learning the framework thoroughly, understanding all features, reference documentation

### [Quick Examples](quick-examples.md)
**Minimal working examples for common use cases**

- Basic setup patterns
- Content assignment shortcuts
- Formatting quick reference
- Complete example with output
- Copy-paste ready code snippets

**Best for:** Getting started quickly, quick reference during development

## Getting Started

1. **New users**: Start with [Quick Examples](quick-examples.md) to get up and running
2. **Detailed learning**: Read the full [Usage Patterns Guide](usage-patterns.md)
3. **Reference**: Bookmark both files for development reference

## Framework Workflow

```
1. Define stages in YAML → 2. Generate Python classes → 3. Build prompts
   stages.yaml           →   structured-prompt generate  →   StructuredPromptFactory
```

## Core Concepts Quick Reference

- **Stages**: Hierarchical structure defined in YAML, generated as Python classes
- **Content Assignment**: `prompt[stage] = content` with append/replace semantics
- **Content Types**: Strings, lists, PromptSection objects, mixed content
- **Formatting**: Configurable bullets, indentation, spacing
- **Critical Steps**: Highlighted mandatory actions at root or section level

## Examples Index

| Use Case | Quick Examples | Usage Patterns Guide |
|----------|----------------|---------------------|
| Basic setup | ✓ | ✓ (detailed) |
| Content assignment | ✓ | ✓ (comprehensive) |
| Nested stages | ✓ | ✓ (detailed) |
| Formatting options | ✓ | ✓ (complete) |
| Critical steps | ✓ | ✓ (detailed) |
| Real-world examples | - | ✓ (multiple) |
| CLI usage | - | ✓ |
| Advanced patterns | - | ✓ |

## Additional Resources

- **Tests**: `/tests/test_dynamic_prompt_builder.py` - Comprehensive test examples
- **Generated Stages**: `/tests/stubs/prompt_structure.py` - Example of generated stage classes
- **Source Code**: `/src/structured_prompt/` - Full implementation
- **CLI Help**: `structured-prompt --help` - Command line usage

---

For questions or issues, please refer to the project's main documentation or create an issue in the repository.
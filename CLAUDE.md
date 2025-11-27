# CLAUDE.md - AI Assistant Guide for Structured Prompt Framework

## Project Overview

The **Structured Prompt Framework** is a Python library that provides extensible, reusable, and standardized prompts for LLMs and AI systems. It enables organizations to maintain consistent, high-quality prompts across teams by providing hierarchical stage systems, flexible content assembly, and type-safe development experience.

**Key Goals:**
- Extensibility: Add/modify prompt sections without breaking core structure
- Reusability: Share and compose prompt components across use cases
- Standardization: Enforce consistent prompt structure within organizations
- LLM-Friendly: Enable AI systems to understand and modify prompts programmatically

## Project Structure

```
src/structured_prompt/
├── __init__.py                     # Main exports and package interface
├── cli.py                         # Command-line interface
├── dynamic_prompt_builder.py      # Dynamic prompt building functionality
├── stage_contract.py              # Stage definition contracts
├── builder/                       # Core prompt building system
│   ├── __init__.py
│   ├── structured_prompt_factory.py  # Main factory class
│   ├── sections.py                # Section handling
│   ├── items.py                   # Item management
│   ├── helpers.py                 # Utility functions
│   ├── preferences.py             # Formatting preferences
│   └── root.py                    # Root stage handling
└── generator/                     # Code generation system
    ├── __init__.py
    ├── prompt_structure_generator.py  # YAML to Python class generator
    └── prompt_stages_generator.py     # Stage class generation logic
```

## Core Concepts

### 1. Stages System
- **Hierarchical Structure**: Stages can have nested child stages
- **YAML Definition**: Structure defined in YAML, converted to Python classes
- **Type Safety**: Auto-generated classes provide IDE completion and static analysis
- **Fixed Ordering**: Critical sections can be locked to specific positions

### 2. Prompt Assembly
- **Content Types**: Plain text, structured sections, nested components
- **Append vs Replace**: Clear semantics for content modification
- **Metadata Support**: Titles, subtitles, bullet styles
- **Critical Steps**: Highlighted mandatory actions

### 3. Rendering System
- **Configurable Formatting**: Bullet styles, indentation, alignment
- **Hierarchical Bullets**: Different styles for different nesting levels
- **Hanging Alignment**: Multi-line content properly formatted

## Key Components

### StructuredPromptFactory
The main entry point for building prompts:

```python
from structured_prompt import StructuredPromptFactory
from stages import Stages

prompt = StructuredPromptFactory(stage_root=Stages)
prompt[Stages.Objective] = ["Define the goal"]
formatted = prompt.render()
```

### PromptStructureGenerator
Converts YAML stage definitions to Python classes:

```python
from structured_prompt import PromptStructureGenerator

generator = PromptStructureGenerator("stages.yaml")
generator.generate("src/stages.py")
```

### Stage Contract
Defines the interface for stage metadata and hierarchy.

## Development Guidelines

### When Working on This Project

1. **Stage Generation**: Always regenerate stage classes after modifying YAML definitions
2. **Type Safety**: Leverage the type-safe stage references for IDE support
3. **Testing**: Run pytest tests/ to ensure functionality works correctly
4. **Code Quality**: Use ruff for linting, mypy for type checking
5. **Backward Compatibility**: Maintain Python 3.8+ compatibility

### Common Tasks

#### Adding New Features
- Understand the hierarchical stage system before modifying
- Consider impact on both generated code and runtime behavior
- Add tests for new functionality
- Update documentation and examples

#### Modifying Rendering
- Changes to bullet styles and formatting in `builder/preferences.py`
- Rendering logic in `builder/sections.py` and related modules
- Test with various nesting levels and content types

#### Extending CLI
- CLI implementation in `cli.py`
- Follow existing command patterns
- Add help text and validation

### Code Patterns

#### Stage Addressing
```python
# Direct stage reference
prompt[Stages.Objective] = content

# Nested stage reference
prompt[Stages.Planning.Steps] = content

# Ad-hoc sections
prompt[Stages.Output]["Custom Section"] = content
```

#### Content Types
```python
# Simple list
prompt[stage] = ["Item 1", "Item 2"]

# PromptSection with metadata
prompt[stage] = PromptSection(
    title="Section Title",
    subtitle="Additional info",
    bullet_style="*",
    items=["Content"]
)
```

## Testing Strategy

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test full prompt generation workflows
- **CLI Tests**: Verify command-line functionality
- **Type Tests**: Ensure generated code maintains type safety

## Release Process

1. **Version Tagging**: Use git tags (e.g., `v0.3.0`)
2. **Automated Release**: GitHub Actions handles PyPI publishing
3. **Version Management**: Version extracted from git tags during release

## Common Issues & Solutions

### Stage Generation Problems
- Ensure YAML syntax is correct
- Check file paths and permissions
- Verify Python import paths in generated code

### Type Safety Issues
- Regenerate stage classes after YAML changes
- Check mypy configuration for proper type checking
- Ensure imports match generated class structure

### Rendering Problems
- Verify bullet style configurations
- Check nesting depth and indentation settings
- Test with various content types and structures

## Integration Notes

### For LLM Systems
- The framework is designed to be LLM-friendly
- AI systems can understand and modify prompts programmatically
- Use the hierarchical addressing system for precise modifications
- Consider the append vs replace semantics when making changes

### For Organizations
- Define standard templates in YAML
- Generate and distribute stage classes across teams
- Use fixed ordering for critical sections
- Enforce consistency through the type system

## Dependencies

- **PyYAML**: For YAML parsing and stage definition loading
- **Python 3.8+**: Minimum version requirement
- **Development**: pytest, ruff, mypy for testing and quality assurance

## Performance Considerations

- Stage class generation is a build-time operation
- Runtime performance focuses on prompt assembly and rendering
- Memory usage scales with prompt complexity and nesting depth
- Consider caching for frequently used prompt structures
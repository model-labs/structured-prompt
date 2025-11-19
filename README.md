# Structured Prompt Framework

[![CI](https://github.com/model-labs/structured-prompt/actions/workflows/ci.yml/badge.svg)](https://github.com/model-labs/structured-prompt/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/structured-prompt.svg)](https://badge.fury.io/py/structured-prompt)
[![Python Support](https://img.shields.io/pypi/pyversions/structured-prompt.svg)](https://pypi.org/project/structured-prompt/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A framework for creating **extensible**, **reusable**, and **standardized** prompts that can be easily modified by LLMs and adapted across organizations.

## Project Goals

This framework addresses the challenge of maintaining consistent, high-quality prompts across teams and AI systems by providing:

1. **Extensibility** - Add new prompt sections and modify existing ones without breaking the core structure and following the same semantic conventions, bullets indentation etc.
2. **Reusability** - Share and compose prompt components across different use cases and teams
3. **Standardization** - Enforce consistent prompt structure and formatting within your organization
4. **LLM-Friendly** - Enable AI systems to understand and modify prompts programmatically
5. **Self-Introspection** (TBD) - Support APIs to evaluate the rendered prompt for inconsistencies and ambiguities

## Key Features

### 🏗️ **Hierarchical Stage System**
- Define canonical prompt stages in YAML (e.g., Objective, Planning, Execution, Output)
- Auto-generate type-safe, IDE-friendly stage classes
- Support both predefined stages and ad-hoc sections

### 📝 **Flexible Content Assembly**
- Mix plain text, structured sections, and nested components
- Append or replace content with clear semantics
- Support metadata like titles, subtitles, and bullet styles

### 🎯 **Organization Templates**
- Define organization-specific prompt templates in YAML
- Enforce consistent structure while allowing customization
- Support fixed ordering for critical sections

### 🔧 **Developer Experience**
- Full IDE autocompletion and static analysis
- Type-safe stage references
- Clear separation between structure and content

## Quick Start

### 1. Define Your Prompt Structure

Create a YAML file defining your organization's prompt template:

```yaml
# stages.yaml
stages:
  objective:
    display: "Objective"
    description: "Define the goal and scope"
    order: fixed
    order_index: 0
  
  planning:
    display: "Planning"
    description: "Outline the approach"
    children:
      steps:
        display: "Steps"
        description: "Detailed execution steps"
  
  execution:
    display: "Execution"
    description: "How to carry out the plan"
  
  output:
    display: "Output"
    description: "Format and structure results"
```

### 2. Generate Stage Classes

Using the command-line tool:

```bash
structured-prompt generate stages.yaml -o src/stages.py
```

Or programmatically:

```python
from structured_prompt import PromptStructureGenerator

generator = PromptStructureGenerator("stages.yaml")
generator.generate("src/stages.py")
```

### 3. Build Your Prompt

The framework supports multiple ways to define a prompt. In most cases assigning an array would extend the existing prompt rather than override it:

```python
from structured_prompt import StructuredPromptFactory, PromptSection
from stages import Stages

# Create a structured prompt
prompt = StructuredPromptFactory(stage_root=Stages)

# Add content to stages
prompt[Stages.Objective] = [
    "Analyze the provided incident and identify root causes",
    "Provide actionable recommendations for resolution"
]

# Add nested content
prompt[Stages.Planning.Steps] = [
    "Start with tracing tools",
    "Follow with metrics analysis",
    "End with infrastructure investigation"
]

# Add ad-hoc sections
prompt[Stages.Output]["Developer Notes"] = [
    "Include code snippets and configuration examples",
    "Provide step-by-step resolution instructions"
]
```

### 4. Render the Prompt

```python
# Get the formatted prompt
formatted_prompt = prompt.render()

print(formatted_prompt)
```

**Output:**
```
1. Objective
  - Analyze the provided incident and identify root causes
  - Provide actionable recommendations for resolution

2. Planning
  - Investigation Plan
    * Review system logs and metrics
    * Analyze error patterns and correlations
    * Identify potential infrastructure issues
  - Steps
    * Start with tracing tools
    * Follow with metrics analysis
    * End with infrastructure investigation

3. Output
  - Developer Notes
    * Include code snippets and configuration examples
    * Provide step-by-step resolution instructions
```

## Architecture

### Stage Model (Auto-generated)
- **Input**: YAML structure definition
- **Output**: Static Python classes with metadata
- **Benefits**: IDE autocompletion, type safety, predictable imports

### Prompt Assembly Layer
- **Purpose**: Compose prompts by addressing stages and adding content
- **Features**: 
  - Hierarchical addressing (`Stages.Planning.Steps`)
  - Append vs. replace semantics
  - Order guarantees for fixed sections
  - Idempotent operations

### Rendering System
- **Purpose**: Convert structured content to formatted text
- **Features**:
  - Configurable bullet styles and indentation
  - Hanging alignment for multi-line content
  - Critical step highlighting
  - Customizable formatting preferences

## Advanced Usage

### Critical Steps
Highlight mandatory actions within your prompt:

```python
prompt.add_critical_step("VERIFY ASSUMPTIONS", "Always validate data sources before proceeding")
prompt[Stages.Execution].add_critical_step("SAFETY CHECK", "Confirm no production impact before changes")
```

### Custom Bullet Styles
Control formatting at the section level:

```python
prompt[Stages.ToolReference] = PromptSection(
    bullet_style=None,  # No bullets for children
    subtitle="Format: [tool|purpose|inputs|notes]",
    items=[
        "[tracing|service analysis|scope|run first]",
        "[metrics|correlation|scope|run after tracing]"
    ]
)
```

### Fixed Ordering
Ensure critical sections appear in specific positions:

```python
# In your YAML:
tool_reference:
  order: fixed
  order_index: 3  # Always appears 4th in the prompt
```

## Organization Integration

### Template Standardization
1. **Define Core Template**: Create a YAML file with your organization's standard prompt structure
2. **Generate Stage Classes**: Run the generator to create type-safe stage classes
3. **Distribute**: Share the generated classes across teams
4. **Enforce**: Use the framework to ensure all prompts follow the same structure

### LLM Modifications
The framework enables AI systems to:
- Understand prompt structure through the stage hierarchy
- Add or modify content while maintaining consistency
- Validate changes against the organization's template
- Generate new prompt variations programmatically

## Installation

```bash
pip install structured-prompt
```

For development:

```bash
git clone https://github.com/model-labs/structured-prompt
cd structured-prompt
pip install -e ".[dev]"
```

## CLI Reference

The `structured-prompt` command-line tool provides utilities for working with the framework.

### Getting Help

```bash
# Show all available commands
structured-prompt --help

# Show help for a specific command
structured-prompt generate --help
```

### Generate Command

Generate Python stage classes from a YAML definition:

```bash
# Basic usage
structured-prompt generate stages.yaml -o src/stages.py

# With custom paths
structured-prompt generate config/prompt_structure.yaml -o myapp/prompts/stages.py
```

**Arguments:**
- `input` - Path to the input YAML file containing stage definitions
- `-o, --output` - Path where the generated Python file should be written

## Development

### Running Tests
```bash
pytest tests/
```

### Linting and Type Checking
```bash
# Run ruff linter
ruff check src/

# Run type checker
mypy src/structured_prompt
```

### Generating Stages

Using the CLI tool:

```bash
structured-prompt generate stages.yaml -o src/stages.py
```

Or programmatically:

```python
from structured_prompt import PromptStructureGenerator

generator = PromptStructureGenerator("stages.yaml")
generator.generate("src/stages.py")
```

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository** and create a feature branch
2. **Follow the existing code structure** and patterns
3. **Add tests** for new features (we aim for high test coverage)
4. **Run the test suite** and ensure all tests pass
5. **Run linters** (`ruff check src/`) to ensure code quality
6. **Update documentation** for API changes
7. **Submit a pull request** with a clear description of changes

### CI/CD

All pull requests automatically run:
- **Tests** on Python 3.13
- **Linting** with ruff
- **Type checking** with mypy
- **Package build** validation

The CI must pass before merging.

### Releasing

To create a new release:

1. **Create a git tag** with the version (e.g., `v0.3.0`):
   ```bash
   git tag v0.3.0
   git push origin v0.3.0
   ```

2. **Create a GitHub release** from the tag

3. The workflow will automatically:
   - Extract the version from the tag
   - Update `pyproject.toml` and `__init__.py`
   - Build the package
   - Publish to PyPI and TestPyPI

**Note**: The version in the code doesn't need to be manually updated - it's extracted from the git tag during release.

## License

[MIT](https://github.com/model-labs/structured-prompt/blob/main/LICENSE)

---

This framework transforms prompt management from an ad-hoc process into a systematic, maintainable system that scales with your organization's needs.

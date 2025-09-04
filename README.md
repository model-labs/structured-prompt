# Structured Prompt Framework

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

```python
from src.generator.prompt_structure_generator import PromptStructureGenerator

generator = PromptStructureGenerator("stages.yaml")
generator.generate("src/stages.py")
```

### 3. Build Your Prompt

The framework supports multiple ways to define a prompt. In most cases assigning an array would extend the existing prompt rather than override it:

```python
from src.builder.dynamic_prompt_builder import DigmaStructuredPrompt, PromptSection
from src.stages import Stages

# Create a structured prompt
prompt = DigmaStructuredPrompt(stage_root=Stages)

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
pip install -r requirements.txt
```

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Generating Stages
```bash
python -m src.generator.prompt_structure_generator --input stages.yaml --output src/stages.py
```

## Contributing

1. Follow the existing code structure and patterns
2. Add tests for new features
3. Update documentation for API changes
4. Ensure generated code follows the established format

## License

[MIT](https://github.com/model-labs/structured-prompt/blob/main/LICENSE)

---

This framework transforms prompt management from an ad-hoc process into a systematic, maintainable system that scales with your organization's needs.

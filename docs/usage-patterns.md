# Structured Prompt Framework - Usage Patterns Guide

This guide demonstrates common usage patterns for the Structured Prompt Framework with practical examples showing different syntaxes and approaches for building structured prompts.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Stage Definition & Generation](#stage-definition--generation)
3. [Basic Content Assignment](#basic-content-assignment)
4. [Content Types and Syntaxes](#content-types-and-syntaxes)
5. [Hierarchical Stage Addressing](#hierarchical-stage-addressing)
6. [Content Assignment Semantics](#content-assignment-semantics)
7. [Formatting and Styling](#formatting-and-styling)
8. [Critical Steps and Mandatory Actions](#critical-steps-and-mandatory-actions)
9. [Advanced Usage Patterns](#advanced-usage-patterns)
10. [CLI Usage](#cli-usage)
11. [Complete Examples](#complete-examples)

## Quick Start

### Installation and Basic Setup

```python
from structured_prompt import StructuredPromptFactory, PromptSection
from stages import Stages  # Your generated stage classes

# Create a prompt builder
prompt = StructuredPromptFactory(stage_root=Stages)

# Add content to stages
prompt[Stages.Objective] = ["Define the goal", "Establish success criteria"]
prompt[Stages.Planning] = ["Step 1: Analyze", "Step 2: Execute"]

# Render the formatted prompt
output = prompt.render_prompt()
print(output)
```

**Output:**
```
1. Objective
  - Define the goal
  - Establish success criteria

2. Planning
  - Step 1: Analyze
  - Step 2: Execute
```

## Stage Definition & Generation

### 1. Define Stages in YAML

Create a `stages.yaml` file with your prompt structure:

```yaml
# stages.yaml
Objective:
  __doc__: "Defines the goal and success criteria"

Planning:
  __doc__: "Outlines the approach"
  Steps:
    __doc__: "Detailed execution steps"
  Resources:
    __doc__: "Required resources and tools"

Output:
  __doc__: "Result formatting"
  Template:
    __doc__: "Output structure"
  Rules:
    __doc__: "Formatting requirements"

ToolReference:
  order: fixed        # Fixed position in output
  order_index: 3      # Always appears 4th (0-indexed)
  __doc__: "Available tools catalog"
```

### 2. Generate Python Classes

```bash
# Using CLI
structured-prompt generate stages.yaml -o src/stages.py

# Programmatically
from structured_prompt import PromptStructureGenerator

generator = PromptStructureGenerator("stages.yaml")
generator.generate("src/stages.py")
```

### 3. Generated Stage Structure

The generated classes provide type-safe, hierarchical stage references:

```python
# Auto-generated in stages.py
class Stages:
    class Objective:
        __stage_display__ = "Objective"
        pass

    class Planning:
        __stage_display__ = "Planning"
        class Steps:
            __stage_display__ = "Steps"
            pass
        class Resources:
            __stage_display__ = "Resources"
            pass
```

## Basic Content Assignment

### Simple List Assignment

```python
# Lists are the most common content type
prompt[Stages.Objective] = [
    "Investigate system performance issues",
    "Identify root cause of slowdowns",
    "Provide actionable recommendations"
]

prompt[Stages.Planning] = [
    "Collect performance metrics",
    "Analyze system logs",
    "Review recent changes"
]
```

### Single String Assignment

```python
# Strings are automatically wrapped in PromptText
prompt[Stages.Objective] = "Resolve the customer-reported outage"

# Multiple single assignments append content
prompt[Stages.Planning] = "Phase 1: Investigation"
prompt[Stages.Planning] = "Phase 2: Resolution"
prompt[Stages.Planning] = "Phase 3: Prevention"
```

## Content Types and Syntaxes

### 1. Plain Strings and Lists

```python
# Simple strings
prompt[Stages.Objective] = "Main goal"

# String lists
prompt[Stages.Planning] = [
    "Step 1: Assessment",
    "Step 2: Analysis",
    "Step 3: Implementation"
]
```

### 2. PromptText Objects

```python
from structured_prompt import PromptText

# Explicit PromptText for advanced control
prompt[Stages.Output] = [
    PromptText("Use Markdown formatting throughout"),
    PromptText("Include code blocks for technical details")
]
```

### 3. PromptSection Objects

```python
# Structured sections with metadata
prompt[Stages.Output] = PromptSection(
    title="Incident Report Template",
    subtitle="Required sections for all incidents",
    bullet_style="*",  # Force asterisk bullets
    items=[
        "Executive Summary",
        "Technical Details",
        "Resolution Steps",
        "Prevention Measures"
    ]
)
```

### 4. Tuple Shorthand

```python
# Tuple format: (title, items, optional_subtitle)
prompt[Stages.Planning] = (
    "Investigation Plan",
    ["Check logs", "Review metrics", "Interview stakeholders"]
)

prompt[Stages.Output] = (
    "Report Format",
    ["Summary", "Details", "Recommendations"],
    "Use this exact structure"
)
```

### 5. Mixed Content Types

```python
# Combine different content types
prompt[Stages.AdaptiveExecution] = [
    PromptText("Follow the planned approach, but remain flexible"),
    PromptSection(
        "Special Scenarios",
        subtitle="Handle these cases differently:",
        items=[
            "High-priority incidents: escalate immediately",
            "Security issues: follow security protocols",
            "Data corruption: stop and backup first"
        ]
    ),
    "Document all deviations with justification"
]
```

## Hierarchical Stage Addressing

### Direct Nested References

```python
# Single-step deep reference (auto-creates parents)
prompt[Stages.Output.Template] = [
    "Incident Summary",
    "Root Cause Analysis",
    "Resolution Timeline"
]

# Even deeper nesting
prompt[Stages.Planning.Steps.Investigation] = [
    "Gather initial data",
    "Form hypothesis"
]
```

### Two-Step Hierarchical Access

```python
# Equivalent to direct reference above
prompt[Stages.Output][Stages.Output.Template] = [
    "Incident Summary",
    "Root Cause Analysis",
    "Resolution Timeline"
]

# Access parent first, then child
output_section = prompt[Stages.Output]
output_section[Stages.Output.Rules] = [
    "Use Markdown format",
    "Include timestamps",
    "Add severity level"
]
```

### Ad-Hoc Sections

```python
# Mix predefined stages with custom sections
prompt[Stages.Planning] = ["Standard planning steps"]

# Add custom subsection to predefined stage
prompt[Stages.Planning]["Contingency Plans"] = [
    "Plan A: Normal resolution",
    "Plan B: Emergency rollback",
    "Plan C: Escalation path"
]

# Completely custom top-level section
prompt["PostIncidentReview"] = [
    "Schedule review meeting",
    "Document lessons learned",
    "Update procedures"
]
```

## Content Assignment Semantics

### Append vs Replace Behavior

#### Append (Default for Lists and Strings)

```python
# First assignment creates section
prompt[Stages.Planning] = ["Step 1", "Step 2"]

# Second assignment APPENDS content
prompt[Stages.Planning] = ["Step 3", "Step 4"]

# Result: Planning contains Steps 1, 2, 3, and 4
# Multiple string assignments also append
prompt[Stages.Output] = "Primary output format"
prompt[Stages.Output] = "Secondary considerations"  # Appended
```

#### Replace (When Assigning PromptSection Objects)

```python
# Initial content
prompt[Stages.Planning] = ["Original step 1", "Original step 2"]

# Assigning PromptSection object REPLACES entire content
prompt[Stages.Planning] = PromptSection(
    title="Revised Planning",
    items=["New step 1", "New step 2", "New step 3"]
)

# Result: Only "New step 1", "New step 2", "New step 3" remain
```

#### Single Item to Multiple Items (NEW)

**When appending to single items, bullets automatically appear for all items:**

```python
# Start with single item (no bullet)
prompt[Stages.Planning] = ["Initial step"]
# Renders: 1. Planning
#            Initial step

# Append another item → bullets appear for both
prompt[Stages.Planning] = ["Second step"]
# Renders: 1. Planning
#            - Initial step
#            - Second step
```

### Automatic Hierarchy Creation

```python
# Deep assignment automatically creates parent stages
prompt[Stages.Output.Template.Header] = ["Title", "Date", "Severity"]

# Creates this hierarchy even if Output and Template weren't assigned:
# Output -> Template -> Header
```

## Formatting and Styling

### Custom Indentation Preferences

```python
from structured_prompt import IndentationPreferences

# Custom formatting settings
custom_prefs = IndentationPreferences(
    spaces_per_level=4,                           # 4 spaces per indent level
    progression=("loweralpha", "dash", "star"),   # a., b., c. then - then *
    fallback="dash",                              # Default bullet style
    blank_line_between_top=True                   # Blank lines between sections
)

prompt = StructuredPromptFactory(
    prefs=custom_prefs,
    stage_root=Stages
)
```

### Bullet Style Control

#### Automatic Single Item Behavior (NEW)

**Single items automatically render without bullets, while multiple items get bullets:**

```python
# Single item - no bullet, just indentation
prompt[Stages.Objective] = ["Single goal"]
# Output: 1. Objective
#           Single goal

# Multiple items - automatic bullets
prompt[Stages.Planning] = ["Step 1", "Step 2"]
# Output: 1. Planning
#           - Step 1
#           - Step 2
```

#### Manual Bullet Control

```python
# No bullets for children (maintains indentation)
prompt[Stages.ToolReference] = PromptSection(
    bullet_style=None,
    subtitle="Format: [name|purpose|input|notes]",
    items=[
        "[trace_analyzer|RCA tool|incident_id|Run first]",
        "[metrics_viewer|Performance data|time_range|After tracing]",
        "[log_parser|Error detection|log_files|Run last]"
    ]
)

# Force specific bullet style (overrides single-item behavior)
prompt[Stages.Planning] = PromptSection(
    bullet_style="*",  # Force asterisks regardless of level
    items=["Task A", "Task B", "Task C"]
)

# Use default progression (respects single-item behavior)
prompt[Stages.Steps] = PromptSection(
    bullet_style=True,  # Use configured progression
    items=["Step 1", "Step 2", "Step 3"]
)
```

#### Bullet Behavior Rules

1. **Single items**: No bullets by default (maintains proper indentation)
2. **Multiple items**: Automatic bullets using progression
3. **`bullet_style=None`**: Overrides both - never shows bullets
4. **Explicit `bullet_style`**: Overrides single-item behavior
5. **Appending**: Single item becomes multiple → bullets appear for all items

### Bullet Progression Examples

```python
# Default progression: ("number", "dash", "star", "loweralpha")

prompt[Stages.Planning] = [
    "Main item",  # 1. Main item
    PromptSection("Sub-category", items=[
        "Sub item 1",  # - Sub item 1
        "Sub item 2",  # - Sub item 2
        PromptSection("Deep section", items=[
            "Deep item 1",  # * Deep item 1
            "Deep item 2"   # * Deep item 2
        ])
    ])
]
```

## Critical Steps and Mandatory Actions

### Root-Level Critical Steps

```python
# Appears after prologue, before any sections
prompt.add_critical_step(
    "VERIFY SCOPE",
    "Confirm incident scope before proceeding with investigation"
)

prompt.add_critical_step(
    "BACKUP FIRST",
    "Always backup current state before making changes"
)
```

### Section-Level Critical Steps

```python
# Add critical step to specific section
prompt[Stages.Planning].add_critical_step(
    "APPROVAL REQUIRED",
    "Get manager approval before implementing high-risk changes"
)

prompt[Stages.Execution].add_critical_step(
    "MONITOR CLOSELY",
    "Watch key metrics during implementation"
)
```

### Critical Steps Rendering

```
!!! MANDATORY STEP [VERIFY SCOPE] !!!
Confirm incident scope before proceeding with investigation
!!! END MANDATORY STEP !!!

1. Planning
  - !!! MANDATORY STEP [APPROVAL REQUIRED] !!!
    Get manager approval before implementing high-risk changes
    !!! END MANDATORY STEP !!!
  - Regular planning step 1
  - Regular planning step 2
```

## Advanced Usage Patterns

### Role and Prologue

```python
# Create prompt with role and prologue
prompt = StructuredPromptFactory(
    role="Senior Site Reliability Engineer",
    prologue="Production Incident Response Protocol",
    stage_root=Stages
)

# Or set role later
prompt.set_role("Database Administrator")
```

**Rendering Order:**
1. Role (as `**Role Text**`)
2. Prologue
3. Root-level critical steps
4. Sections (ordered by stage configuration)

### Fixed Stage Ordering

```yaml
# In stages.yaml - ensure certain stages appear in specific positions
ToolReference:
  order: fixed
  order_index: 3  # Always appears 4th (0-indexed)
  __doc__: "Tools catalog"
```

```python
# Assignment order doesn't matter for fixed stages
prompt[Stages.Planning] = ["Plan A"]        # Assigned first
prompt[Stages.ToolReference] = ["Tool 1"]   # Assigned later but appears at position 4
prompt[Stages.Objective] = ["Goal"]         # Assigned last but appears first
```

### Complex Nested Structures

```python
# Build complex hierarchical content
prompt[Stages.Investigation] = [
    PromptSection(
        "Primary Investigation",
        items=[
            PromptSection(
                "System Metrics",
                subtitle="Check these metrics in order:",
                items=[
                    "CPU utilization (last 4 hours)",
                    "Memory usage patterns",
                    "Disk I/O bottlenecks",
                    "Network throughput"
                ]
            ),
            PromptSection(
                "Application Logs",
                bullet_style=None,  # No bullets for log format
                items=[
                    "ERROR: Database connection timeout",
                    "WARN: High response times detected",
                    "INFO: Deployment completed successfully"
                ]
            )
        ]
    ),
    "Cross-reference findings with recent changes"
]
```

### Dynamic Content Building

```python
# Build content programmatically
steps = ["Identify", "Analyze", "Resolve", "Verify"]
prompt[Stages.Planning] = [f"Step {i+1}: {step}" for i, step in enumerate(steps)]

# Conditional content
if incident_severity == "high":
    prompt[Stages.Planning].add_critical_step(
        "ESCALATE IMMEDIATELY",
        "Notify on-call manager within 15 minutes"
    )

# Template-based content
regions = ["us-east-1", "us-west-2", "eu-west-1"]
prompt[Stages.Monitoring] = [
    f"Check {region} health dashboard" for region in regions
]
```

## CLI Usage

### Basic Commands

```bash
# Generate stage classes from YAML
structured-prompt generate stages.yaml -o src/stages.py

# Generate with custom paths
structured-prompt generate config/prompt_structure.yaml -o myapp/stages.py

# Get help
structured-prompt generate --help
```

### Integration in Build Process

```bash
# In your Makefile or build script
generate-stages:
	structured-prompt generate specs/stages.yaml -o src/app/stages.py

# In package.json (Node.js projects)
{
  "scripts": {
    "generate-stages": "structured-prompt generate stages.yaml -o src/stages.py"
  }
}
```

## Complete Examples

### Example 1: Incident Response Prompt

```python
from structured_prompt import StructuredPromptFactory, PromptSection, IndentationPreferences
from stages import Stages

# Create incident response prompt
prompt = StructuredPromptFactory(
    role="Senior Site Reliability Engineer",
    prologue="Production Incident Response - Follow this protocol exactly",
    stage_root=Stages,
    prefs=IndentationPreferences(blank_line_between_top=True)
)

# Add critical verification step
prompt.add_critical_step(
    "VERIFY PERMISSIONS",
    "Confirm you have necessary access before proceeding"
)

# Define objective
prompt[Stages.Objective] = [
    "Restore service to normal operation",
    "Minimize customer impact and downtime",
    "Collect data for post-incident review"
]

# Investigation plan
prompt[Stages.Planning] = [
    PromptSection(
        "Triage Phase",
        subtitle="Complete within first 15 minutes:",
        items=[
            "Assess severity and impact scope",
            "Notify stakeholders per escalation matrix",
            "Start incident war room if severity >= P1"
        ]
    ),
    PromptSection(
        "Investigation Phase",
        items=[
            "Check service health dashboards",
            "Review recent deployment activity",
            "Analyze error rates and latency metrics",
            "Examine infrastructure alerts"
        ]
    )
]

# Tool reference with no bullets
prompt[Stages.ToolReference] = PromptSection(
    bullet_style=None,
    subtitle="Available tools [name|purpose|priority]:",
    items=[
        "[datadog|metrics & alerts|HIGH]",
        "[kibana|log analysis|MEDIUM]",
        "[grafana|system monitoring|HIGH]",
        "[pagerduty|incident management|CRITICAL]"
    ]
)

# Output format
prompt[Stages.Output] = [
    PromptSection(
        "Incident Summary",
        items=[
            "Timeline of events",
            "Root cause analysis",
            "Resolution actions taken",
            "Customer impact assessment"
        ]
    ),
    "Submit incident report within 24 hours"
]

# Quality gates
prompt[Stages.QualityGates].add_critical_step(
    "CUSTOMER VALIDATION",
    "Confirm with customer that service is restored before closing"
)

prompt[Stages.QualityGates] = [
    "All alerts cleared",
    "Metrics back to baseline",
    "No error spikes in logs",
    "Customer confirmation received"
]

print(prompt.render_prompt())
```

### Example 2: Code Review Prompt

```python
# Code review assistant prompt
prompt = StructuredPromptFactory(
    role="Senior Software Engineer",
    prologue="Code Review Guidelines - Ensure quality and maintainability",
    stage_root=Stages
)

prompt[Stages.Objective] = "Provide thorough, constructive code review feedback"

prompt[Stages.ReviewCriteria] = [
    PromptSection(
        "Functional Review",
        items=[
            "Logic correctness and edge case handling",
            "Performance implications",
            "Security considerations",
            "Error handling and recovery"
        ]
    ),
    PromptSection(
        "Code Quality",
        items=[
            "Readability and maintainability",
            "Adherence to coding standards",
            "Test coverage adequacy",
            "Documentation completeness"
        ]
    )
]

prompt[Stages.Output] = PromptSection(
    "Review Format",
    subtitle="Structure feedback as follows:",
    items=[
        "**Summary**: Overall assessment and key points",
        "**Strengths**: What's done well",
        "**Issues**: Problems requiring changes (P0=blocking, P1=important, P2=minor)",
        "**Suggestions**: Improvements and alternatives",
        "**Approval Status**: Approve/Request Changes/Comment"
    ]
)

print(prompt.render_prompt())
```

### Example 3: Data Analysis Prompt

```python
# Data analysis workflow
prompt = StructuredPromptFactory(
    role="Data Scientist",
    stage_root=Stages
)

prompt[Stages.Objective] = [
    "Analyze dataset to identify key patterns and insights",
    "Provide actionable business recommendations"
]

# Multi-phase approach
prompt[Stages.Methodology] = [
    ("Exploratory Data Analysis", [
        "Dataset overview and structure",
        "Missing value analysis",
        "Distribution analysis",
        "Correlation identification"
    ]),
    ("Statistical Analysis", [
        "Hypothesis testing",
        "Significance testing",
        "Confidence intervals",
        "Effect size calculations"
    ]),
    ("Visualization", [
        "Key finding charts",
        "Interactive dashboards",
        "Executive summary plots"
    ])
]

# Custom tools section
prompt["AnalysisTools"] = PromptSection(
    bullet_style="*",
    items=[
        "Python: pandas, numpy, scipy",
        "Visualization: matplotlib, seaborn, plotly",
        "Statistics: statsmodels, scikit-learn",
        "Reporting: jupyter notebooks, markdown"
    ]
)

print(prompt.render_prompt())
```

## Best Practices

### 1. Stage Design

- **Keep stages focused**: Each stage should have a clear, single purpose
- **Use hierarchical organization**: Group related concepts under parent stages
- **Consider fixed ordering**: Use `order: fixed` for stages that must appear in specific positions
- **Document stages**: Include `__doc__` strings for stage purpose

### 2. Content Organization

- **Start with lists**: Use simple string lists for most content
- **Add structure when needed**: Use PromptSection for complex hierarchies
- **Mix content types thoughtfully**: Combine different content types when it improves clarity
- **Use critical steps sparingly**: Reserve for truly mandatory actions

### 3. Formatting

- **Consistent bullet styles**: Define a clear bullet progression
- **Appropriate indentation**: Use 2-4 spaces per level for readability
- **Strategic blank lines**: Use blank lines between major sections
- **Meaningful titles**: Use descriptive section titles and subtitles

### 4. Development Workflow

- **Version control YAML**: Keep stage definitions in version control
- **Regenerate after changes**: Always regenerate Python classes after YAML changes
- **Test stage structure**: Write tests to verify prompt structure and content
- **Document usage patterns**: Maintain examples of how stages should be used

---

This guide covers the major usage patterns for the Structured Prompt Framework. For additional details, see the API documentation and test files for more advanced scenarios.
# Quick Usage Examples

This file provides minimal working examples for common use cases.

## Basic Setup

```python
from structured_prompt import StructuredPromptFactory, PromptSection
from stages import Stages  # Generated from your YAML

prompt = StructuredPromptFactory(stage_root=Stages)
```

## Content Assignment Patterns

### Single vs Multiple Items (NEW)
```python
# Single item - no bullet
prompt[Stages.Objective] = ["Single goal"]

# Multiple items - automatic bullets
prompt[Stages.Planning] = ["Step A", "Step B"]
```

### Simple Lists
```python
prompt[Stages.Objective] = ["Goal 1", "Goal 2"]  # Multiple items → bullets
prompt[Stages.Planning] = ["Step A", "Step B"]   # Multiple items → bullets
```

### Single Strings (Auto-Append)
```python
prompt[Stages.Notes] = "First note"
prompt[Stages.Notes] = "Second note"  # Appends to first
```

### Nested Stages (Auto-Create Parents)
```python
prompt[Stages.Output.Template] = ["Section 1", "Section 2"]
# Creates Output -> Template hierarchy automatically
```

### Structured Sections
```python
prompt[Stages.Planning] = PromptSection(
    "Detailed Plan",
    subtitle="Execute in order:",
    items=["Task 1", "Task 2", "Task 3"]
)
```

### Mixed Content
```python
prompt[Stages.Rules] = [
    "Basic rule",
    PromptSection("Special Cases", items=["Case A", "Case B"]),
    "Final rule"
]
```

## Formatting Options

### Custom Bullets
```python
# No bullets (maintains indentation)
prompt[Stages.Tools] = PromptSection(
    bullet_style=None,
    items=["tool1|purpose", "tool2|purpose"]
)

# Force specific bullet
prompt[Stages.Tasks] = PromptSection(
    bullet_style="*",
    items=["Task 1", "Task 2"]
)
```

### Custom Indentation
```python
from structured_prompt import IndentationPreferences

custom_prefs = IndentationPreferences(
    spaces_per_level=4,
    progression=("number", "dash", "star")
)

prompt = StructuredPromptFactory(
    prefs=custom_prefs,
    stage_root=Stages
)
```

## Critical Steps
```python
# Root level (appears early)
prompt.add_critical_step("IMPORTANT", "Check this first")

# Section level
prompt[Stages.Planning].add_critical_step("VERIFY", "Confirm before proceeding")
```

## Role and Prologue
```python
prompt = StructuredPromptFactory(
    role="Senior Engineer",
    prologue="System Maintenance Protocol",
    stage_root=Stages
)
```

## Complete Example Output

Input:
```python
prompt = StructuredPromptFactory(
    role="DevOps Engineer",
    prologue="Deployment Checklist",
    stage_root=Stages
)

prompt.add_critical_step("BACKUP", "Create backup before proceeding")

# Single item - no bullet
prompt[Stages.Objective] = ["Complete deployment without downtime"]

# Multiple items - bullets
prompt[Stages.PreDeployment] = [
    "Run tests",
    "Check dependencies"
]

prompt[Stages.Deployment] = PromptSection(
    "Release Process",
    subtitle="Execute steps in order:",
    items=[
        "Deploy to staging",
        "Run smoke tests",
        "Deploy to production"
    ]
)
```

Output:
```
**DevOps Engineer**

Deployment Checklist

!!! MANDATORY STEP [BACKUP] !!!
Create backup before proceeding
!!! END MANDATORY STEP !!!

1. Objective
  Complete deployment without downtime

2. Pre Deployment
  - Run tests
  - Check dependencies

3. Deployment
  - Release Process
      Execute steps in order:
    * Deploy to staging
    * Run smoke tests
    * Deploy to production
```

**Note**: The `Objective` section has a single item, so it renders without a bullet while maintaining proper indentation. The `Pre Deployment` section has multiple items, so they get bullets automatically.
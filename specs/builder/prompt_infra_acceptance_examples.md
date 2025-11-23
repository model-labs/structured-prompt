
# Prompt Infra — Acceptance Examples

This document demonstrates **example usage** of the prompt framework and the **expected rendering** for each case.  
Each example highlights a **principle** of the system.

> Note: Examples assume:
> - `from dynamic_prompt.dynamic_prompt_builder import StructuredPromptFactory, PromptSection, PromptText`
> - `from hyper_reasoning.prompts.prompt_stages import Stages`
> - Default `IndentationPreferences`: top-level: `1., 2., 3.`, children: `-`, then `*`, then `a.`
> - `blank_line_between_top = True`

---

## 1) Append when setting an **array** value
**Principle:** Assigning a `List[ItemLike]` to a section **appends** items to that section (creating it first if absent).

**Code**
```python
prompt = StructuredPromptFactory(stage_root=Stages)

prompt[Stages.AdaptiveExecution] = [
    PromptSection(
        name=Stages.AdaptiveExecution.AdaptiveExecutionRule,
        subtitle="Follow your planned steps in order, but you MAY:",
        items=[
            "Insert new tool calls if new evidence suggests they will help meet the objective.",
            "Skip planned tool calls if earlier results make them unnecessary or irrelevant.",
            "Repeat a tool call with modified parameters if previous output was insufficient.",
            "Document every deviation in execution_log with: {reason_for_change, impact_on_plan}.",
            "Use all RELEVANT investigators from TOOLS; re-call them if the picture is unclear or confidence < High.",
        ],
    ),
]
# Appending more content to the same section key:
prompt[Stages.AdaptiveExecution] = [
    "Do not repeat steps already done. If you tried ~8 variations and failed, report what you learned."
]
```

**Expected rendering (excerpt)**
```
1. Adaptive Execution
  - Adaptive Execution Rule — Follow your planned steps in order, but you MAY:
    * Insert new tool calls if new evidence suggests they will help meet the objective.
    * Skip planned tool calls if earlier results make them unnecessary or irrelevant.
    * Repeat a tool call with modified parameters if previous output was insufficient.
    * Document every deviation in execution_log with: {reason_for_change, impact_on_plan}.
    * Use all RELEVANT investigators from TOOLS; re-call them if the picture is unclear or confidence < High.
  - Do not repeat steps already done. If you tried ~8 variations and failed, report what you learned.
```

---

## 2) **Replace** when setting a `PromptSection` object
**Principle:** Assigning a `PromptSection(...)` directly to a stage key **replaces** that section (set semantics).  
The **key** is taken from the dictionary key; the `PromptSection.title` is kept if provided; otherwise it’s derived from the key’s display.

**Code**
```python
prompt = StructuredPromptFactory(stage_root=Stages)

# First assignment:
prompt[Stages.QualityGates] = [
    "Coverage: Start with tracing, then metrics, then infra; do not skip layers without a reason.",
]

# Replace with a PromptSection (set semantics):
prompt[Stages.QualityGates] = PromptSection(
    title="Quality Gates (Thoroughness & Clarity)",
    items=[
        "Coverage: Start with tracing tools, then metrics, then infra tools; do not skip layers unless you log a reason.",
        "Corroboration: Cite ≥2 independent signals for high confidence.",
    ],
)
```

**Expected rendering (excerpt)**
```
1. Quality Gates (Thoroughness & Clarity)
  - Coverage: Start with tracing tools, then metrics, then infra tools; do not skip layers unless you log a reason.
  - Corroboration: Cite ≥2 independent signals for high confidence.
```

---

## 3) Append when setting a **string** value
**Principle:** Assigning a plain `str` to a stage key **appends** it as a `PromptText` to that section.

**Code**
```python
prompt = StructuredPromptFactory(stage_root=Stages)

prompt[Stages.Output][Stages.Output.OutputTemplateRules] = [
    "Always format answers using valid Markdown.",
    "Use **bold** or *italic* for emphasis",
]
# later...
prompt[Stages.Output][Stages.Output.OutputTemplateRules] = "Use headings (#, ##, etc.)"
```

**Expected rendering (excerpt)**
```
1. Output
  - Output Template Rules
    * Always format answers using valid Markdown.
    * Use **bold** or *italic* for emphasis
    * Use headings (#, ##, etc.)
```

---

## 4) **Take key value from dictionary key**
**Principle:** When assigning via `prompt[<key>] = ...`, the section’s **key** is derived from the dictionary key (stage class) and the **title** is derived from its display (e.g., `Output Template Rules`).

**Code**
```python
prompt = StructuredPromptFactory(stage_root=Stages)

prompt[Stages.Output][Stages.Output.OutputTemplate] = [
    "Incident Scope",
    "Root Cause",
]
```

**Expected rendering (excerpt)**
```
1. Output
  - Output Template
    * Incident Scope
    * Root Cause
```

---

## 5) Hierarchical addressing — **with** and **without** explicit parent
**Principle:** You can reference a deep stage directly and the framework auto-creates ancestors.  
`prompt[Stages.Output.OutputTemplateRules]` and  
`prompt[Stages.Output][Stages.Output.OutputTemplateRules]` are equivalent.

**Code**
```python
prompt = StructuredPromptFactory(stage_root=Stages)

# Direct deep reference:
prompt[Stages.Output.OutputTemplateRules] = ["Always format answers using valid Markdown."]

# Equivalent two-step form:
prompt[Stages.Output][Stages.Output.OutputTemplateRules] = ["Use headings (#, ##, etc.)"]
```

**Expected rendering (excerpt)**
```
1. Output
  - Output Template Rules
    * Always format answers using valid Markdown.
    * Use headings (#, ##, etc.)
```

---

## 6) Nested sections created with a `PromptSection` **value**
**Principle:** Passing a `PromptSection(name=<Stage or str>, items=[...])` allows embedding subsections in one shot.

**Code**
```python
prompt = StructuredPromptFactory(stage_root=Stages)

prompt[Stages.AdaptiveExecution] = [
    PromptSection(
        Stages.AdaptiveExecution.SpecialCases,
        [
            PromptSection(
                "Infrastructure Discrepancy",
                subtitle=(
                    "If metrics/traces show clear errors but infrastructure analysis "
                    "(e.g., k8s_issue_investigation_tool) shows no problems:"
                ),
                items=[
                    "Call infrastructure tools with scope='OUTSIDE_THE_BOX'.",
                    "Purpose: identify overlooked infra issues.",
                    "Document in execution_log whether you took this action and why.",
                ],
            )
        ],
    ),
]
```

**Expected rendering (excerpt)**
```
1. Adaptive Execution
  - Special Cases
    * Infrastructure Discrepancy — If metrics/traces show clear errors but infrastructure analysis (e.g., k8s_issue_investigation_tool) shows no problems:
      a. Call infrastructure tools with scope='OUTSIDE_THE_BOX'.
      b. Purpose: identify overlooked infra issues.
      c. Document in execution_log whether you took this action and why.
```

---

## 7) Bullet style control — **no bullets for children**
**Principle:** `bullet_style=None` on a section **keeps the section’s own bullet** but **suppresses bullets for its children**, while maintaining indentation/hanging alignment.

**Code**
```python
prompt = StructuredPromptFactory(stage_root=Stages)

prompt[Stages.ToolReference] = PromptSection(
    bullet_style=None,  # suppress bullets for children
    subtitle="RULE: [name|purpose|required_inputs|notes]",
    items=[
        "[tracing|service-level RCA|objective,scope|MUST_RUN_FIRST]",
        "[metrics|scale & correlation|objective,scope|RUN_AFTER_TRACING]",
        "[infra|infra-level RCA|objective,scope|RUN_LAST]",
    ],
)
```

**Expected rendering**
```
1. ToolReference — RULE: [name|purpose|required_inputs|notes]
    [tracing|service-level RCA|objective,scope|MUST_RUN_FIRST]
    [metrics|scale & correlation|objective,scope|RUN_AFTER_TRACING]
    [infra|infra-level RCA|objective,scope|RUN_LAST]
```

---

## 8) Fixed top-level ordering
**Principle:** If a top-level stage is marked `order: fixed` in YAML (e.g., `ToolReference`), it renders in that order **regardless of assignment time**.

**Code (order of assignments is intentionally shuffled)**
```python
prompt = StructuredPromptFactory(stage_root=Stages)

prompt[Stages.Planning] = ["Plan step A"]
prompt[Stages.QualityGates] = ["Gate A"]
# Late assignment of a fixed-order top-level:
prompt[Stages.ToolReference] = ["[tracing|...]", "[metrics|...]", "[infra|...]"]
prompt[Stages.Scoping] = ["Define scope"]
```

**Expected top-level order (example)**
```
1. Objective
2. Global Rules
3. Operating Principles
4. ToolReference
5. Scoping
6. Planning
...
```

---

## 9) Critical steps (section-level and root-level)
**Principle:** `add_critical_step(title, description)` renders a mandatory block **under the section heading**.  
If added to the root prompt, it renders **after the prologue and before the first section**.

**Code**
```python
prompt = StructuredPromptFactory(stage_root=Stages, prologue="K8s Resolver Prompt")

# Root-level critical step
prompt.add_critical_step("CHECK OTHER NAMESPACES AND FLAGS", "Explore other namespaces and compare configs.")

# Section-level critical step
prompt[Stages.Scoping].add_critical_step("SCOPE SUPREMACY", "If specific issues are provided, investigate ONLY those.")
prompt[Stages.Scoping] = ["Record incident summary and objective."]
```

**Expected rendering (top excerpt)**
```
K8s Resolver Prompt

!!! MANDATORY STEP [CHECK OTHER NAMESPACES AND FLAGS] !!!
Explore other namespaces and compare configs.
!!! END MANDATORY STEP !!!

1. Scoping
  - !!! MANDATORY STEP [SCOPE SUPREMACY] !!!
    If specific issues are provided, investigate ONLY those.
    !!! END MANDATORY STEP !!!
  - Record incident summary and objective.
```

---

## 10) Mixing `PromptText`, `str`, and nested sections
**Principle:** Any `ItemLike` is acceptable: `PromptText("...")`, plain strings, or nested `PromptSection` objects.

**Code**
```python
prompt = StructuredPromptFactory(stage_root=Stages)

prompt[Stages.Output] = [
    PromptText("Use Markdown throughout."),
    PromptSection("Output Template", items=["Incident Scope", "Root Cause", "Evidence"]),
    "Avoid plain text only."
]
```

**Expected rendering (excerpt)**
```
1. Output
  - Use Markdown throughout.
  - Output Template
    * Incident Scope
    * Root Cause
    * Evidence
  - Avoid plain text only.
```

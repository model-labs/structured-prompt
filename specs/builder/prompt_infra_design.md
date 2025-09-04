# Prompt Infrastructure Design Document

## Requirements

1. **Extend hard coded hierarchy of agreed upon prompt stages**  
   Authors should be able to work with a stable hierarchy of canonical stages that are predefined and agreed upon.

2. **Extend the prompt with arbitrary stages**  
   Beyond canonical stages, authors should be able to introduce ad-hoc or dynamic sections seamlessly.

3. **Define prompts in multiple ways**  
   - As plain strings  
   - As structured sections with metadata (e.g., title, subtitle, bullet style)  
   - As collections of items (lists, tuples, nested sections)

4. **Address bullet styles, indentation, and hanging**  
   The system must support configurable bullet progression, indentation, and hanging alignment for multi-line entries.

---

## High-Level Architecture

### 1) Stage Model (Auto-generated)
**Purpose:** Provide a stable, human-readable, autocompletable *vocabulary* of stages and their hierarchy.

- **Inputs:** A declarative stage structure (YAML) that describes the canonical stages, their parent/child relationships, display names, and ordering hints.
- **Outputs:** A static, importable “stage model” that exposes the agreed hierarchy as navigable symbols (e.g., `Planning`, `AdaptiveExecution.AfterToolExecution`).
- **Behavior:**
  - Encodes hierarchy (parent/child) and optional top-level ordering preferences (e.g., “fixed order”).
  - Carries documentation for each stage (used for human comprehension and tooling).
- **Why:** Authors get reliable, IDE-friendly handles for composing prompts; the rest of the system can reason about hierarchy and ordering without parsing arbitrary strings.

---

### 2) Prompt Assembly Layer
**Purpose:** Let authors compose prompts by *addressing* stages and adding content—without worrying about rendering details.

- **Inputs:** 
  - Stage references (from the Stage Model) and/or ad-hoc stage names.
  - Content items (plain text, nested sections, or collections).
  - Optional presentation preferences (e.g., bullet rules, subtitles).
- **Outputs:** A structured, tree-like prompt document (not yet formatted).
- **Behavior:**
  - **Stage addressing:** Content can be attached via canonical stages *or* arbitrary ad-hoc stages.  
    - If a parent stage is referenced implicitly through a child, the parent is created on demand.
  - **Append vs. replace semantics:** Assigning a new list appends; assigning a full section can replace when explicitly set to do so (clear and predictable).
  - **Order guarantees:** Top-level “fixed order” stages always render in the canonical order; others follow insertion order.
  - **Idempotence:** Re-adding content to the same stage appends, unless explicitly instructed to replace.


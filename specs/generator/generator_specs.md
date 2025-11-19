Got it — thanks for the concrete sample. Here’s a tight, behavior-first design note that matches the actual generated format you’re producing right now (the one with pass bodies and metadata assigned after class definitions).

⸻

Stage Code Generator — What It Emits & How It’s Used

Scope

This doc describes what the generator outputs and how the prompt infra consumes it, using the exact structure shown in your current generated file (i.e., nested classes with pass, then metadata assignments below).

⸻

What the generator emits (matching your sample)

1) Root container and nested stage classes
	•	A single Stages root with top-level nested classes (e.g., Objective, GlobalRules, ToolReference, …).
	•	Some stages have nested classes (e.g., AdaptiveExecution.AfterToolExecution).
	•	Bodies contain only pass.

# AUTO-GENERATED: DO NOT EDIT BY HAND
class Stages:
    """Auto-generated hierarchical stage tree."""
    pass

    class ToolReference:
        """ Serves as a catalog … """
        __stage_display__ = 'ToolReference'
        pass

    class AdaptiveExecution:
        """ Describes how and when to adjust the plan … """
        __stage_display__ = 'Adaptive Execution'
        pass

        class AfterToolExecution:
            """ States how results should be validated … """
            __stage_display__ = 'After Tool Execution'
            pass

2) Per-class metadata (assigned after definitions)

For every class (top-level and nested):
	•	__stage_root__ → Stages
	•	__stage_parent__ → parent class (or Stages if top-level)
	•	__children__ → tuple of immediate child classes (or () if none)
	•	__stage_display__ → already set inside class from YAML label (e.g., "Global Rules")

For top-level classes only:
	•	__order_fixed__ → True iff order: fixed in YAML (else False)
	•	__order_index__ → top-level index from YAML (0-based)

Additionally:
	•	Stages.__top_levels__ → tuple of all top-level stage classes in YAML order
	•	Stages.__fixed_top_order__ → tuple of the top-level classes that are fixed

Example (exact style you have):

Stages.ToolReference.__stage_root__   = Stages
Stages.ToolReference.__stage_parent__ = Stages
Stages.ToolReference.__children__     = ()

Stages.ToolReference.__order_fixed__  = True
Stages.ToolReference.__order_index__  = 3

Stages.__top_levels__      = (Stages.Objective, Stages.GlobalRules, ..., Stages.QualityGates,)
Stages.__fixed_top_order__ = (Stages.ToolReference,)

3) Design Decisions (Why this approach)
	•	Static classes instead of dynamic wiring
		Guarantees IDE autocompletion, static analysis, and predictable imports.
	•	Dual identity (display vs key)
		Keeps the human-friendly label and a robust lowercased programmatic key.
	•	Embedded metadata
		StructuredPromptFactory doesn’t need to be “injected” with a root; all info lives in the generated classes.
	•	Fixed ordering only where needed
		Most sections should remain flexible; pin only those that must be in a fixed position.

⸻

How the prompt infra uses it

Stage identity & display
	•	Display title: __stage_display__ (e.g., "Global Rules").
	•	Programmatic key: the class name lowercased (e.g., GlobalRules → "globalrules").
This keeps human-friendly labels and stable keys separate.

Hierarchy navigation
	•	The infra can derive ancestry/descendants from:
	•	__stage_parent__ and __children__
	•	Or simple attribute navigation (Stages.AdaptiveExecution.AfterToolExecution)

Top-level ordering
	•	If any top-level stage has __order_fixed__ = True, honor __order_index__ for those fixed ones.
	•	All non-fixed top-level sections preserve append/insertion order.
	•	The generator also provides Stages.__top_levels__ and Stages.__fixed_top_order__ to make this cheap to compute without scanning class dicts.

Interop with StructuredPromptFactory
	•	Users can assign with either the stage class or strings interchangeably:

prompt[Stages.ToolReference] = PromptSection(…)       # replace semantics
prompt[Stages.AdaptiveExecution.AfterToolExecution] = ["…"]  # append items
prompt[Stages.Output]["My Extra Section"] = ["…"]     # arbitrary child under Output


	•	When assigning a nested stage (leaf), infra auto-creates any missing parents, using:
	•	__stage_display__ for titles
	•	class-name-lowercase for keys

⸻

Responsibilities split
	•	YAML: structure and docs (__doc__), plus optional order: fixed for top-levels.
	•	Generator (this module): emits static classes + post-assigns metadata + emits ordering tuples.
	•	Prompt infra:
	•	Key normalization (class-name-lowercase)
	•	Title rendering (use __stage_display__)
	•	Replace vs append semantics on __setitem__
	•	Ordering at render time (use __fixed_top_order__ and insertion order for others)
	•	Bullets/indent/hanging (render concern, not generator)

⸻

Minimal usage examples (aligned with your output)

# Replace a top-level section with a PromptSection
prompt[Stages.ToolReference] = PromptSection(
    subtitle="RULE: [name|purpose|required_inputs|notes]",
    bullet_style=None,  # controls bullets for this section’s children at render time
    items=[
        "[tracing tools|…|objective,scope|MUST_RUN_FIRST]",
        "[metrics tools|…|objective,scope|RUN_AFTER_TRACING]",
    ],
)

# Append plain strings to a nested leaf – parents auto-created if missing
prompt[Stages.AdaptiveExecution.AfterToolExecution] = [
    "Validate intended new state after each action.",
    "If failed, re-collect logs and re-analyze.",
]

# Arbitrary child under a known parent
prompt[Stages.Output]["Developer Handoff Notes"] = [
    "Checklist for ops handover…",
]


⸻

Notes & common pitfalls
	•	Don’t edit the generated file by hand. Update the YAML and re-generate.
	•	__stage_display__ is the only human-facing title source; keep it clean in YAML.
	•	If you see a fixed section rendering last, check that:
	•	It appears in Stages.__fixed_top_order__
	•	It has __order_fixed__ == True and a sensible __order_index__
	•	Your renderer actually uses these attributes before falling back to insertion order.

⸻

If you want, I can turn this into a docs/stage_generator.md file exactly as above.
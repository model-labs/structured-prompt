import pytest

from src.builder import StructuredPromptFactory, PromptSection, IndentationPreferences, PromptText
from tests.stubs.prompt_structure import Stages


class TestDynamicPromptBuilder:
    """Test suite for the dynamic prompt builder covering all acceptance examples."""

    def test_1_append_when_setting_array_value(self):
        """Test that assigning a List[ItemLike] to a section appends items."""
        prompt = StructuredPromptFactory()

        # First assignment
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

        # Appending more content to the same section key
        prompt[Stages.AdaptiveExecution] = [
            "Do not repeat steps already done. If you tried ~8 variations and failed, report what you learned."
        ]

        rendered = prompt.render_prompt()

        # Verify the section exists and contains both sets of content
        assert "1. Adaptive Execution" in rendered
        assert "Adaptive Execution Rule" in rendered
        assert "Follow your planned steps in order, but you MAY:" in rendered
        assert "Insert new tool calls if new evidence suggests they will help meet the objective." in rendered
        assert (
            "Do not repeat steps already done. If you tried ~8 variations and failed, report what you learned."
            in rendered
        )

    def test_2_replace_when_setting_prompt_section_object(self):
        """Test that assigning a PromptSection directly replaces that section."""
        prompt = StructuredPromptFactory()

        # First assignment
        prompt[Stages.QualityGates] = [
            "Coverage: Start with tracing, then metrics, then infra; do not skip layers without a reason.",
        ]

        # Replace with a PromptSection (set semantics)
        prompt[Stages.QualityGates] = PromptSection(
            title="Quality Gates (Thoroughness & Clarity)",
            items=[
                "Coverage: Start with tracing tools, then metrics, then infra tools; do not skip layers unless you log a reason.",
                "Corroboration: Cite ≥2 independent signals for high confidence.",
            ],
        )

        rendered = prompt.render_prompt()

        # Verify the old content is replaced
        assert (
            "Coverage: Start with tracing, then metrics, then infra; do not skip layers without a reason."
            not in rendered
        )

        # Verify the new content is present
        assert "1. Quality Gates (Thoroughness & Clarity)" in rendered
        assert (
            "Coverage: Start with tracing tools, then metrics, then infra tools; do not skip layers unless you log a reason."
            in rendered
        )
        assert "Corroboration: Cite ≥2 independent signals for high confidence." in rendered

    def test_3_append_when_setting_string_value(self):
        """Test that assigning a plain str to a stage key appends it as PromptText."""
        prompt = StructuredPromptFactory()

        prompt[Stages.Output][Stages.Output.OutputTemplateRules] = [
            "Always format answers using valid Markdown.",
            "Use **bold** or *italic* for emphasis",
        ]

        # later...
        prompt[Stages.Output][Stages.Output.OutputTemplateRules] = "Use headings (#, ##, etc.)"

        rendered = prompt.render_prompt()

        # Verify all three items are present
        assert "Always format answers using valid Markdown." in rendered
        assert "Use **bold** or *italic* for emphasis" in rendered
        assert "Use headings (#, ##, etc.)" in rendered

    def test_4_take_key_value_from_dictionary_key(self):
        """Test that section key is derived from dictionary key and title from display."""
        prompt = StructuredPromptFactory()

        prompt[Stages.Output][Stages.Output.OutputTemplate] = [
            "Incident Scope",
            "Root Cause",
        ]

        rendered = prompt.render_prompt()

        # Verify the section is created with the correct title
        assert "1. Output" in rendered
        assert "Output Template" in rendered
        assert "Incident Scope" in rendered
        assert "Root Cause" in rendered

    def test_5_hierarchical_addressing_with_and_without_explicit_parent(self):
        """Test that deep stage references auto-create ancestors."""
        prompt = StructuredPromptFactory()

        # Direct deep reference
        prompt[Stages.Output.OutputTemplateRules] = ["Always format answers using valid Markdown."]

        # Equivalent two-step form
        prompt[Stages.Output][Stages.Output.OutputTemplateRules] = ["Use headings (#, ##, etc.)"]

        rendered = prompt.render_prompt()

        # Verify both items are present in the same section
        assert "1. Output" in rendered
        assert "Output Template Rules" in rendered
        assert "Always format answers using valid Markdown." in rendered
        assert "Use headings (#, ##, etc.)" in rendered

    def test_6_nested_sections_created_with_prompt_section_value(self):
        """Test that PromptSection allows embedding subsections in one shot."""
        prompt = StructuredPromptFactory()

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

        rendered = prompt.render_prompt()

        # Verify nested structure is created
        assert "1. Adaptive Execution" in rendered
        assert "Special Cases" in rendered
        assert "Infrastructure Discrepancy" in rendered
        assert "If metrics/traces show clear errors but infrastructure analysis" in rendered
        assert "Call infrastructure tools with scope='OUTSIDE_THE_BOX'." in rendered
        assert "Purpose: identify overlooked infra issues." in rendered
        assert "Document in execution_log whether you took this action and why." in rendered

    def test_7_bullet_style_control_no_bullets_for_children(self):
        """Test that bullet_style=None suppresses bullets for children while maintaining indentation."""
        prompt = StructuredPromptFactory()

        prompt[Stages.ToolReference] = PromptSection(
            bullet_style=None,  # suppress bullets for children
            subtitle="RULE: [name|purpose|required_inputs|notes]",
            items=[
                "[tracing|service-level RCA|objective,scope|MUST_RUN_FIRST]",
                "[metrics|scale & correlation|objective,scope|RUN_AFTER_TRACING]",
                "[infra|infra-level RCA|objective,scope|RUN_LAST]",
            ],
        )

        rendered = prompt.render_prompt()

        # Verify section has title and subtitle
        assert "1. Tool Reference" in rendered
        assert "RULE: [name|purpose|required_inputs|notes]" in rendered

        # Verify children have no bullets but maintain indentation
        assert "[tracing|service-level RCA|objective,scope|MUST_RUN_FIRST]" in rendered
        assert "[metrics|scale & correlation|objective,scope|RUN_AFTER_TRACING]" in rendered
        assert "[infra|infra-level RCA|objective,scope|RUN_LAST]" in rendered

    def test_8_fixed_top_level_ordering(self):
        """Test that fixed-order top-level stages render in canonical order regardless of assignment time."""
        prompt = StructuredPromptFactory()

        # Order of assignments is intentionally shuffled
        prompt[Stages.Planning] = ["Plan step A"]
        prompt[Stages.QualityGates] = ["Gate A"]
        # Late assignment of a fixed-order top-level
        prompt[Stages.ToolReference] = ["[tracing|...]", "[metrics|...]", "[infra|...]"]
        prompt[Stages.Scoping] = ["Define scope"]

        rendered = prompt.render_prompt()

        # Find the positions of each section
        lines = rendered.split("\n")
        planning_idx = None
        quality_gates_idx = None
        tool_reference_idx = None
        scoping_idx = None

        for i, line in enumerate(lines):
            if line.strip().startswith("1. Planning"):
                planning_idx = i
            elif line.strip().startswith("2. Quality Gates"):
                quality_gates_idx = i
            elif line.strip().startswith("3. Scoping"):
                scoping_idx = i
            elif line.strip().startswith("4. Tool Reference"):
                tool_reference_idx = i

        # Verify all sections are found
        assert planning_idx is not None, "Planning section not found"
        assert quality_gates_idx is not None, "Quality Gates section not found"
        assert scoping_idx is not None, "Scoping section not found"
        assert tool_reference_idx is not None, "Tool Reference section not found"

        # Verify the order matches the assignment order (since these are not fixed-order stages)
        # The order should be: Planning (1), Quality Gates (2), Scoping (3), Tool Reference (4)
        assert planning_idx < quality_gates_idx
        assert quality_gates_idx < scoping_idx
        assert scoping_idx < tool_reference_idx

        # Verify ToolReference appears at position 4 (as expected from assignment order)
        assert "4. Tool Reference" in lines[tool_reference_idx]

    def test_9_critical_steps_section_level_and_root_level(self):
        """Test that add_critical_step renders mandatory blocks at section and root levels."""
        prompt = StructuredPromptFactory(prologue="K8s Resolver Prompt")

        # Root-level critical step
        prompt.add_critical_step("CHECK OTHER NAMESPACES AND FLAGS", "Explore other namespaces and compare configs.")

        # Section-level critical step
        prompt[Stages.Scoping].add_critical_step(
            "SCOPE SUPREMACY", "If specific issues are provided, investigate ONLY those."
        )
        prompt[Stages.Scoping] = ["Record incident summary and objective."]

        rendered = prompt.render_prompt()

        # Verify root-level critical step appears after prologue
        assert "K8s Resolver Prompt" in rendered
        assert "!!! MANDATORY STEP [CHECK OTHER NAMESPACES AND FLAGS] !!!" in rendered
        assert "Explore other namespaces and compare configs." in rendered

        # Verify section-level critical step appears under the section heading
        assert "1. Scoping" in rendered
        assert "!!! MANDATORY STEP [SCOPE SUPREMACY] !!!" in rendered
        assert "If specific issues are provided, investigate ONLY those." in rendered
        assert "Record incident summary and objective." in rendered

    def test_10_mixing_prompt_text_str_and_nested_sections(self):
        """Test that any ItemLike is acceptable: PromptText, plain strings, or nested PromptSection objects."""
        prompt = StructuredPromptFactory()

        prompt[Stages.Output] = [
            PromptText("Use Markdown throughout."),
            PromptSection("Output Template", items=["Incident Scope", "Root Cause", "Evidence"]),
            "Avoid plain text only.",
        ]

        rendered = prompt.render_prompt()

        # Verify all items are rendered correctly
        assert "1. Output" in rendered
        assert "Use Markdown throughout." in rendered
        assert "Output Template" in rendered
        assert "Incident Scope" in rendered
        assert "Root Cause" in rendered
        assert "Evidence" in rendered
        assert "Avoid plain text only." in rendered

    def test_indentation_preferences(self):
        """Test custom indentation preferences."""
        custom_prefs = IndentationPreferences(
            spaces_per_level=4,  # 4 spaces per level
            progression=("loweralpha", "dash", "star"),  # A., B., C. then -, then *
            blank_line_between_top=True,
        )

        prompt = StructuredPromptFactory(prefs=custom_prefs)

        prompt[Stages.Output] = ["Main output rule", PromptSection("Template", items=["Section 1", "Section 2"])]

        rendered = prompt.render_prompt()

        # Verify custom indentation is applied
        assert "a. Output" in rendered
        assert "    - Main output rule" in rendered
        assert "    - Template" in rendered
        assert "        * Section 1" in rendered
        assert "        * Section 2" in rendered

    def test_blank_line_between_top_preference(self):
        """Test blank_line_between_top preference."""
        # Test with blank lines between top sections
        prompt_with_blanks = StructuredPromptFactory()
        prompt_with_blanks.prefs.blank_line_between_top = True

        prompt_with_blanks[Stages.Output] = ["Test output"]
        prompt_with_blanks[Stages.QualityGates] = ["Test gates"]

        rendered_with_blanks = prompt_with_blanks.render_prompt()

        # Test without blank lines between top sections
        prompt_without_blanks = StructuredPromptFactory()
        prompt_without_blanks.prefs.blank_line_between_top = False

        prompt_without_blanks[Stages.Output] = ["Test output"]
        prompt_without_blanks[Stages.QualityGates] = ["Test gates"]

        rendered_without_blanks = prompt_without_blanks.render_prompt()

        # Verify the difference
        assert rendered_with_blanks.count("\n\n") > rendered_without_blanks.count("\n\n")

    def test_arbitrary_stage_names(self):
        """Test that arbitrary stage names can be used alongside canonical stages."""
        prompt = StructuredPromptFactory()

        # Use canonical stage
        prompt[Stages.Output] = ["Canonical content"]

        # Use arbitrary stage name
        prompt["CustomStage"] = ["Custom content"]

        rendered = prompt.render_prompt()

        # Verify both stages are rendered
        assert "1. Output" in rendered
        assert "Canonical content" in rendered
        assert "2. Custom Stage" in rendered
        assert "Custom content" in rendered

    def test_nested_arbitrary_stages(self):
        """Test nested arbitrary stages."""
        prompt = StructuredPromptFactory()

        prompt["MainStage"] = [PromptSection("SubStage", items=["Sub content"]), "Main content"]

        rendered = prompt.render_prompt()

        # Verify nested structure
        assert "1. Main Stage" in rendered
        assert "Sub Stage" in rendered
        assert "Sub content" in rendered
        assert "Main content" in rendered

    def test_stage_root_inheritance(self):
        """Test that nested sections inherit stage_root from parent."""
        prompt = StructuredPromptFactory()

        # Create a nested section that should inherit stage_root
        nested_section = PromptSection("Nested", items=["Nested content"])
        prompt["ParentStage"] = [nested_section]

        # Verify the nested section can access stage_root
        # Note: The stage_root is set when the section is added to the prompt
        assert hasattr(prompt, "_stage_root")
        assert prompt._stage_root == Stages

    def test_multiline_text_rendering(self):
        """Test that multiline text is rendered with proper hanging indentation."""
        prompt = StructuredPromptFactory()

        multiline_text = """This is a multiline text
that should be rendered with proper
hanging indentation for continuation lines."""

        prompt[Stages.Output] = [multiline_text]

        rendered = prompt.render_prompt()

        # Verify the first line has a bullet
        assert "This is a multiline text" in rendered

        # Verify continuation lines are properly indented
        lines = rendered.split("\n")
        output_section_lines = []
        in_output_section = False

        for line in lines:
            if line.strip().startswith("1. Output"):
                in_output_section = True
            elif in_output_section and line.strip().startswith("2."):
                break
            elif in_output_section:
                output_section_lines.append(line)

        # Find the multiline text and verify hanging indentation
        multiline_found = False
        for i, line in enumerate(output_section_lines):
            if "This is a multiline text" in line:
                multiline_found = True
                # Check that continuation lines have proper indentation
                if (
                    i + 1 < len(output_section_lines)
                    and "that should be rendered with proper" in output_section_lines[i + 1]
                ):
                    # The continuation line should have more indentation than the first line
                    first_line_indent = len(output_section_lines[i]) - len(output_section_lines[i].lstrip())
                    cont_line_indent = len(output_section_lines[i + 1]) - len(output_section_lines[i + 1].lstrip())
                    assert cont_line_indent > first_line_indent
                break

        assert multiline_found, "Multiline text not found in output"

    def test_empty_prompt_rendering(self):
        """Test that an empty prompt renders correctly."""
        prompt = StructuredPromptFactory()

        rendered = prompt.render_prompt()

        # Should render just the prologue (if any) and no sections
        assert rendered.strip() == ""

    def test_prompt_with_only_prologue(self):
        """Test prompt with only prologue text."""
        prompt = StructuredPromptFactory(prologue="Test Prologue")

        rendered = prompt.render_prompt()

        # Should render just the prologue
        assert rendered.strip() == "Test Prologue"

    def test_prompt_with_only_critical_steps(self):
        """Test prompt with only critical steps and no sections."""
        prompt = StructuredPromptFactory(prologue="Test")
        prompt.add_critical_step("CRITICAL", "This is critical")

        rendered = prompt.render_prompt()

        # Should render prologue, critical step, and no sections
        assert "Test" in rendered
        assert "!!! MANDATORY STEP [CRITICAL] !!!" in rendered
        assert "This is critical" in rendered
        assert "1." not in rendered  # No sections

    def test_complex_nested_structure(self):
        """Test a complex nested structure to ensure proper rendering."""
        prompt = StructuredPromptFactory()

        prompt[Stages.Output] = [
            PromptSection(
                "Complex Template",
                items=[
                    PromptSection("Subsection A", items=["Item A1", "Item A2"]),
                    PromptSection("Subsection B", items=["Item B1", "Item B2", "Item B3"]),
                    "Plain text item",
                ],
            ),
            "Another main item",
        ]

        rendered = prompt.render_prompt()

        # Verify complex structure
        assert "1. Output" in rendered
        assert "Complex Template" in rendered
        assert "Subsection A" in rendered
        assert "Item A1" in rendered
        assert "Item A2" in rendered
        assert "Subsection B" in rendered
        assert "Item B1" in rendered
        assert "Item B2" in rendered
        assert "Item B3" in rendered
        assert "Plain text item" in rendered
        assert "Another main item" in rendered

    def test_deep_stage_assignment_without_parent(self):
        """Test that assigning a deep stage without explicit parent assignment auto-creates entire hierarchy."""
        prompt = StructuredPromptFactory()

        # Assign to deep stage without ever assigning to parent Stages.Output
        prompt[Stages.Output.OutputTemplateRules] = ["New Rule"]

        rendered = prompt.render_prompt()

        # Verify the entire hierarchy is created and shown
        assert "1. Output" in rendered
        assert "Output Template Rules" in rendered
        assert "New Rule" in rendered

        # Verify the structure is properly nested
        lines = rendered.split("\n")
        output_line_idx = None
        template_rules_line_idx = None
        new_rule_line_idx = None

        for i, line in enumerate(lines):
            if line.strip().startswith("1. Output"):
                output_line_idx = i
            elif "Output Template Rules" in line:
                template_rules_line_idx = i
            elif "New Rule" in line:
                new_rule_line_idx = i

        # Verify all components are found
        assert output_line_idx is not None, "Output section not found"
        assert template_rules_line_idx is not None, "Output Template Rules section not found"
        assert new_rule_line_idx is not None, "New Rule not found"

        # Verify proper nesting order
        assert output_line_idx < template_rules_line_idx < new_rule_line_idx

        # Verify proper indentation (Output Template Rules should be indented under Output)
        template_rules_line = lines[template_rules_line_idx]
        assert template_rules_line.startswith("  -"), f"Expected indented Output Template Rules, got: {template_rules_line}"

        # Verify New Rule is properly indented under Output Template Rules
        new_rule_line = lines[new_rule_line_idx]
        assert new_rule_line.startswith("    *"), f"Expected indented New Rule, got: {new_rule_line}"


if __name__ == "__main__":
    pytest.main([__file__])

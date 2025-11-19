import os
import sys
import tempfile
from pathlib import Path

import pytest

from structured_prompt import StructuredPromptFactory, PromptSection, IndentationPreferences, PromptText
from structured_prompt.generator.prompt_structure_generator import generate_stages_module

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))



class TestGeneratedStagesIntegration:
    """Integration tests that validate generated stages work with prompt infrastructure."""

    def setup_method(self):
        """Set up test fixtures for each test method."""
        # Create a minimal test YAML for testing
        self.test_yaml_content = """
        Objective:
            __doc__: "Defines the mission of the investigation and the boundaries of success."
        Global Rules:
            __doc__: "Declares top-level constraints and priority principles."
        Operating Principles:
            __doc__: "Captures expected reasoning and behavior throughout the investigation."
        ToolReference:
            order: fixed
            order_index: 3
            __doc__: "Serves as a catalog of available tools with their high-level purposes."
        Scoping:
            __doc__: "Records what is in and out of scope for the incident."
        Planning:
            __doc__: "Outlines the intended approach to meet the objective."
        AdaptiveExecution:
            __doc__: "Describes how and when to adjust the plan based on emerging findings."
            AdaptiveExecutionRule:
                __doc__: "States the governing rule for inserting, skipping, or repeating steps."
            BeforeToolExecution:
                __doc__: "States the preparation expectations before invoking a tool."
            AfterToolExecution:
                __doc__: "States how results should be validated and how the plan should be adjusted."
            SpecialCases:
                __doc__: "Handles exceptional scenarios and edge cases during execution."
        Output:
            __doc__: "Groups the schema and conventions for the user-facing result."
            OutputTemplate:
                __doc__: "Specifies the required sections and structure of the final summary."
            OutputTemplateRules:
                __doc__: "Specifies formatting and structural conventions for the final summary."
        QualityGates:
            __doc__: "Represents the final quality verification concept."
        """

        # Create temporary files
        self.yaml_file = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
        self.yaml_file.write(self.test_yaml_content)
        self.yaml_file.flush()

        self.py_file = tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False)
        self.py_file.close()

        # Generate the stages module
        generate_stages_module(Path(self.yaml_file.name), Path(self.py_file.name))

        # Import the generated module
        sys.path.insert(0, str(Path(self.py_file.name).parent))
        import importlib.util

        spec = importlib.util.spec_from_file_location("test_stages", self.py_file.name)
        self.test_stages = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.test_stages)

        # Get the Stages class
        self.Stages = self.test_stages.Stages

    def teardown_method(self):
        """Clean up test fixtures after each test method."""
        # Clean up temporary files
        if hasattr(self, "yaml_file"):
            self.yaml_file.close()
            Path(self.yaml_file.name).unlink()

        if hasattr(self, "py_file"):
            if Path(self.py_file.name).exists():
                Path(self.py_file.name).unlink()

        # Remove from sys.path
        if hasattr(self, "py_file"):
            sys.path.remove(str(Path(self.py_file.name).parent))

    def test_generated_stages_structure(self):
        """Test that the generated stages have the correct structure and metadata."""
        # Check top-level stages exist
        assert hasattr(self.Stages, "Objective")
        assert hasattr(self.Stages, "GlobalRules")
        assert hasattr(self.Stages, "OperatingPrinciples")
        assert hasattr(self.Stages, "ToolReference")
        assert hasattr(self.Stages, "Scoping")
        assert hasattr(self.Stages, "Planning")
        assert hasattr(self.Stages, "AdaptiveExecution")
        assert hasattr(self.Stages, "Output")
        assert hasattr(self.Stages, "QualityGates")

        # Check nested stages exist
        assert hasattr(self.Stages.AdaptiveExecution, "AdaptiveExecutionRule")
        assert hasattr(self.Stages.AdaptiveExecution, "BeforeToolExecution")
        assert hasattr(self.Stages.AdaptiveExecution, "AfterToolExecution")
        assert hasattr(self.Stages.Output, "OutputTemplate")
        assert hasattr(self.Stages.Output, "OutputTemplateRules")

        # Check metadata is properly set - now using humanized display names
        assert self.Stages.Objective.__stage_display__ == "Objective"
        assert self.Stages.GlobalRules.__stage_display__ == "Global Rules"
        assert self.Stages.AdaptiveExecution.__stage_display__ == "Adaptive Execution"

        # Check fixed ordering
        assert self.Stages.ToolReference.__order_fixed__ is True
        assert self.Stages.ToolReference.__order_index__ == 3
        assert self.Stages.Objective.__order_fixed__ is False

        # Check top-level collections
        assert hasattr(self.Stages, "__top_levels__")
        assert hasattr(self.Stages, "__fixed_top_order__")
        assert self.Stages.ToolReference in self.Stages.__fixed_top_order__

    def test_acceptance_example_1_append_array_value(self):
        """Test acceptance example 1: Append when setting array value."""
        prompt = StructuredPromptFactory()

        # First assignment
        prompt[self.Stages.AdaptiveExecution] = [
            PromptSection(
                name=self.Stages.AdaptiveExecution.AdaptiveExecutionRule,
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
        prompt[self.Stages.AdaptiveExecution] = [
            "Do not repeat steps already done. If you tried ~8 variations and failed, report what you learned."
        ]

        rendered = prompt.render_prompt()

        # Verify the section exists and contains both sets of content
        # Now expecting humanized name
        assert "1. Adaptive Execution" in rendered
        # The subtitle is rendered without the em dash, just as a separate line
        assert "Adaptive Execution Rule" in rendered
        assert "Follow your planned steps in order, but you MAY:" in rendered
        assert "Insert new tool calls if new evidence suggests they will help meet the objective." in rendered
        assert (
            "Do not repeat steps already done. If you tried ~8 variations and failed, report what you learned."
            in rendered
        )

    def test_acceptance_example_2_replace_prompt_section(self):
        """Test acceptance example 2: Replace when setting PromptSection object."""
        prompt = StructuredPromptFactory()

        # First assignment
        prompt[self.Stages.QualityGates] = [
            "Coverage: Start with tracing, then metrics, then infra; do not skip layers without a reason.",
        ]

        # Replace with a PromptSection (set semantics)
        prompt[self.Stages.QualityGates] = PromptSection(
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

        # Verify the new content is present - now expecting humanized name
        assert "1. Quality Gates" in rendered
        assert "Quality Gates (Thoroughness & Clarity)" in rendered
        assert (
            "Coverage: Start with tracing tools, then metrics, then infra tools; do not skip layers unless you log a reason."
            in rendered
        )
        assert "Corroboration: Cite ≥2 independent signals for high confidence." in rendered

    def test_acceptance_example_3_append_string_value(self):
        """Test acceptance example 3: Append when setting string value."""
        prompt = StructuredPromptFactory()

        prompt[self.Stages.Output][self.Stages.Output.OutputTemplateRules] = [
            "Always format answers using valid Markdown.",
            "Use **bold** or *italic* for emphasis",
        ]

        # later...
        prompt[self.Stages.Output][self.Stages.Output.OutputTemplateRules] = "Use headings (#, ##, etc.)"

        rendered = prompt.render_prompt()

        # Verify all three items are present
        assert "Always format answers using valid Markdown." in rendered
        assert "Use **bold** or *italic* for emphasis" in rendered
        assert "Use headings (#, ##, etc.)" in rendered

    def test_acceptance_example_4_key_from_dictionary_key(self):
        """Test acceptance example 4: Take key value from dictionary key."""
        prompt = StructuredPromptFactory()

        prompt[self.Stages.Output][self.Stages.Output.OutputTemplate] = [
            "Incident Scope",
            "Root Cause",
        ]

        rendered = prompt.render_prompt()

        # Verify the section is created with the correct title
        assert "1. Output" in rendered
        assert "Output Template" in rendered
        assert "Incident Scope" in rendered
        assert "Root Cause" in rendered

    def test_acceptance_example_5_hierarchical_addressing(self):
        """Test acceptance example 5: Hierarchical addressing with and without explicit parent."""
        prompt = StructuredPromptFactory()

        # Direct deep reference
        prompt[self.Stages.Output.OutputTemplateRules] = ["Always format answers using valid Markdown."]

        # Equivalent two-step form
        prompt[self.Stages.Output][self.Stages.Output.OutputTemplateRules] = ["Use headings (#, ##, etc.)"]

        rendered = prompt.render_prompt()

        # Verify both items are present in the same section
        assert "1. Output" in rendered
        assert "Output Template Rules" in rendered
        assert "Always format answers using valid Markdown." in rendered
        assert "Use headings (#, ##, etc.)" in rendered

    def test_acceptance_example_6_nested_sections(self):
        """Test acceptance example 6: Nested sections created with PromptSection value."""
        prompt = StructuredPromptFactory()

        # Check if SpecialCases exists, if not skip this test
        if not hasattr(self.Stages.AdaptiveExecution, "SpecialCases"):
            pytest.skip("SpecialCases stage not generated")

        prompt[self.Stages.AdaptiveExecution] = [
            PromptSection(
                self.Stages.AdaptiveExecution.SpecialCases,
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

    def test_end_to_end_with_actual_yaml(self):
        """End-to-end test: Generate stages from actual YAML file and validate prompt functionality."""
        # Check if the actual YAML file exists
        actual_yaml_path = Path("specs/prompt_structure/prompt_structure.yaml")
        if not actual_yaml_path.exists():
            pytest.skip(f"Actual YAML file not found at {actual_yaml_path}")

        # Create temporary output file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp_py:
            tmp_py.close()
            tmp_py_path = Path(tmp_py.name)

        try:
            # Generate stages from actual YAML
            generate_stages_module(actual_yaml_path, tmp_py_path)

            # Import the generated module
            sys.path.insert(0, str(tmp_py_path.parent))
            import importlib.util

            spec = importlib.util.spec_from_file_location("actual_stages", tmp_py_path)
            actual_stages_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(actual_stages_module)

            # Get the Stages class
            ActualStages = actual_stages_module.Stages

            # Validate basic structure exists
            assert hasattr(ActualStages, "Objective")
            assert hasattr(ActualStages, "GlobalRules")
            assert hasattr(ActualStages, "OperatingPrinciples")
            assert hasattr(ActualStages, "ToolReference")
            assert hasattr(ActualStages, "Scoping")
            assert hasattr(ActualStages, "Planning")
            assert hasattr(ActualStages, "AdaptiveExecution")
            assert hasattr(ActualStages, "Output")
            assert hasattr(ActualStages, "QualityGates")

            # Test that we can create a prompt with the generated stages
            prompt = StructuredPromptFactory()

            # Add some content to various stages
            prompt[ActualStages.Objective] = "Investigate and resolve the production incident"
            prompt[ActualStages.Scoping] = "Focus on the user-facing API errors"
            prompt[ActualStages.Planning] = [
                "1. Analyze error traces",
                "2. Check infrastructure status",
                "3. Implement fix",
            ]

            # Render the prompt
            rendered = prompt.render_prompt()

            # Validate the rendered output contains our content
            assert "Investigate and resolve the production incident" in rendered
            assert "Focus on the user-facing API errors" in rendered
            assert "1. Analyze error traces" in rendered
            assert "2. Check infrastructure status" in rendered
            assert "3. Implement fix" in rendered

            # Validate stage names are humanized
            assert "1. Objective" in rendered
            assert "2. Scoping" in rendered
            assert "3. Planning" in rendered

            # Clean up sys.path
            sys.path.remove(str(tmp_py_path.parent))

        finally:
            # Clean up temporary file
            if tmp_py_path.exists():
                tmp_py_path.unlink()

    def test_acceptance_example_7_bullet_style_control(self):
        """Test acceptance example 7: Bullet style control - no bullets for children."""
        prompt = StructuredPromptFactory()

        prompt[self.Stages.ToolReference] = PromptSection(
            bullet_style=None,  # suppress bullets for children
            subtitle="RULE: [name|purpose|required_inputs|notes]",
            items=[
                "[tracing|service-level RCA|objective,scope|MUST_RUN_FIRST]",
                "[metrics|scale & correlation|objective,scope|RUN_AFTER_TRACING]",
                "[infra|infra-level RCA|objective,scope|RUN_LAST]",
            ],
        )

        rendered = prompt.render_prompt()

        # Verify section has title and subtitle - now expecting humanized name
        assert "1. Tool Reference" in rendered
        assert "RULE: [name|purpose|required_inputs|notes]" in rendered

        # Verify children have no bullets but maintain indentation
        assert "[tracing|service-level RCA|objective,scope|MUST_RUN_FIRST]" in rendered
        assert "[metrics|scale & correlation|objective,scope|RUN_AFTER_TRACING]" in rendered
        assert "[infra|infra-level RCA|objective,scope|RUN_LAST]" in rendered

    def test_acceptance_example_8_fixed_top_level_ordering(self):
        """Test acceptance example 8: Fixed top-level ordering."""
        prompt = StructuredPromptFactory()

        # Order of assignments is intentionally shuffled
        prompt[self.Stages.Planning] = ["Plan step A"]
        prompt[self.Stages.QualityGates] = ["Gate A"]
        # Late assignment of a fixed-order top-level
        prompt[self.Stages.ToolReference] = ["[tracing|...]", "[metrics|...]", "[infra|...]"]
        prompt[self.Stages.Scoping] = ["Define scope"]

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
            elif line.strip().startswith("3. Tool Reference"):
                tool_reference_idx = i
            elif line.strip().startswith("4. Scoping"):
                scoping_idx = i

        # Verify all sections are found
        assert planning_idx is not None, f"Planning not found in rendered output: {rendered}"
        assert quality_gates_idx is not None, f"Quality Gates not found in rendered output: {rendered}"
        assert tool_reference_idx is not None, f"Tool Reference not found in rendered output: {rendered}"
        assert scoping_idx is not None, f"Scoping not found in rendered output: {rendered}"

        # Verify sections appear in insertion order
        assert planning_idx < quality_gates_idx
        assert quality_gates_idx < tool_reference_idx
        assert tool_reference_idx < scoping_idx

    def test_acceptance_example_9_critical_steps(self):
        """Test acceptance example 9: Critical steps (section-level and root-level)."""
        prompt = StructuredPromptFactory(prologue="K8s Resolver Prompt")

        # Root-level critical step
        prompt.add_critical_step("CHECK OTHER NAMESPACES AND FLAGS", "Explore other namespaces and compare configs.")

        # Section-level critical step
        prompt[self.Stages.Scoping].add_critical_step(
            "SCOPE SUPREMACY", "If specific issues are provided, investigate ONLY those."
        )
        prompt[self.Stages.Scoping] = ["Record incident summary and objective."]

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

    def test_acceptance_example_10_mixing_content_types(self):
        """Test acceptance example 10: Mixing PromptText, str, and nested sections."""
        prompt = StructuredPromptFactory()

        prompt[self.Stages.Output] = [
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

    def test_generated_stages_metadata_integrity(self):
        """Test that all generated stages have complete and correct metadata."""
        # Check all top-level stages have required metadata
        top_level_stages = [
            self.Stages.Objective,
            self.Stages.GlobalRules,
            self.Stages.OperatingPrinciples,
            self.Stages.ToolReference,
            self.Stages.Scoping,
            self.Stages.Planning,
            self.Stages.AdaptiveExecution,
            self.Stages.Output,
            self.Stages.QualityGates,
        ]

        for stage in top_level_stages:
            assert hasattr(stage, "__stage_root__")
            assert hasattr(stage, "__stage_parent__")
            assert hasattr(stage, "__children__")
            assert hasattr(stage, "__stage_display__")
            assert hasattr(stage, "__order_fixed__")
            assert hasattr(stage, "__order_index__")

            # Verify metadata values
            assert stage.__stage_root__ == self.Stages
            assert stage.__stage_parent__ == self.Stages
            assert isinstance(stage.__order_fixed__, bool)
            assert isinstance(stage.__order_index__, int)

        # Check nested stages have correct metadata
        nested_stage = self.Stages.AdaptiveExecution.AdaptiveExecutionRule
        assert nested_stage.__stage_root__ == self.Stages
        assert nested_stage.__stage_parent__ == self.Stages.AdaptiveExecution
        assert nested_stage.__children__ == ()

    def test_generated_stages_ordering_integrity(self):
        """Test that the generated stages have correct ordering metadata."""
        # Check that ToolReference is properly marked as fixed order
        assert self.Stages.ToolReference.__order_fixed__ is True
        assert self.Stages.ToolReference.__order_index__ == 3

        # Check that other stages are not fixed order
        assert self.Stages.Objective.__order_fixed__ is False
        assert self.Stages.Scoping.__order_fixed__ is False

        # Check top-level collections
        assert len(self.Stages.__top_levels__) == 9  # All top-level stages
        assert len(self.Stages.__fixed_top_order__) == 1  # Only ToolReference
        assert self.Stages.ToolReference in self.Stages.__fixed_top_order__

    def test_generated_stages_with_custom_indentation(self):
        """Test that generated stages work correctly with custom indentation preferences."""
        custom_prefs = IndentationPreferences(
            spaces_per_level=4,  # 4 spaces per level
            progression=("loweralpha", "dash", "star"),  # A., B., C. then -, then *
            blank_line_between_top=True,
        )

        prompt = StructuredPromptFactory(prefs=custom_prefs)

        prompt[self.Stages.Output] = ["Main output rule", PromptSection("Template", items=["Section 1", "Section 2"])]

        rendered = prompt.render_prompt()

        # Verify custom indentation is applied
        assert "a. Output" in rendered
        assert "    - Main output rule" in rendered
        assert "    - Template" in rendered
        assert "        * Section 1" in rendered
        assert "        * Section 2" in rendered

    def test_generated_stages_arbitrary_children(self):
        """Test that generated stages can have arbitrary children added."""
        prompt = StructuredPromptFactory()

        # Add arbitrary child under a generated stage
        prompt[self.Stages.Output]["Developer Handoff Notes"] = [
            "Checklist for ops handover",
            "Key decision points documented",
            "Next steps clearly outlined",
        ]

        rendered = prompt.render_prompt()

        # Verify the arbitrary child is rendered
        assert "1. Output" in rendered
        assert "Developer Handoff Notes" in rendered
        assert "Checklist for ops handover" in rendered
        assert "Key decision points documented" in rendered
        assert "Next steps clearly outlined" in rendered


if __name__ == "__main__":
    pytest.main([__file__])

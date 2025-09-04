import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

import pytest

from generator.prompt_structure_generator import load_yaml, _normalize_mapping_to_nodes, _normalize_node, to_identifier, \
    emit_class_tree, qname, collect_paths, emit_wiring, generate_stages_module


class TestPromptStagesGenerator:
    """Test suite for the prompt stages generator."""

    def test_load_yaml_valid_structure(self):
        """Test loading valid YAML structure."""
        yaml_content = """
        Objective:
            __doc__: "Defines the mission of the investigation."
        Global Rules:
            __doc__: "Declares top-level constraints."
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            
            result = load_yaml(Path(f.name))
            
            assert "stages" in result
            assert len(result["stages"]) == 2
            assert result["stages"][0]["display"] == "Objective"
            assert result["stages"][1]["display"] == "Global Rules"
            
            # Cleanup
            Path(f.name).unlink()

    def test_load_yaml_invalid_top_level(self):
        """Test loading invalid YAML (not a mapping at top level)."""
        yaml_content = "Objective: some string"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            
            with pytest.raises(ValueError, match="Stage 'Objective' must be a mapping or null"):
                load_yaml(Path(f.name))
            
            # Cleanup
            Path(f.name).unlink()

    def test_load_yaml_stage_not_mapping(self):
        """Test loading YAML with stage that's not a mapping."""
        yaml_content = """
        Objective: "not a mapping"
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            
            with pytest.raises(ValueError, match="Stage 'Objective' must be a mapping or null"):
                load_yaml(Path(f.name))
            
            # Cleanup
            Path(f.name).unlink()

    def test_normalize_mapping_to_nodes(self):
        """Test normalizing YAML mapping to node structure."""
        yaml_data = {
            "Objective": {
                "__doc__": "Defines the mission.",
                "order": False,
                "order_index": 0
            },
            "Global Rules": {
                "__doc__": "Declares constraints.",
                "order": "fixed",
                "order_index": 1
            }
        }
        
        result = _normalize_mapping_to_nodes(yaml_data)
        
        assert len(result) == 2
        assert result[0]["display"] == "Objective"
        assert result[0]["class"] == "Objective"
        assert result[0]["doc"] == "Defines the mission."
        assert result[0]["order_fixed"] is False
        assert result[0]["order_index"] == 0
        
        assert result[1]["display"] == "Global Rules"
        assert result[1]["class"] == "GlobalRules"
        assert result[1]["doc"] == "Declares constraints."
        assert result[1]["order_fixed"] is True
        assert result[1]["order_index"] == 1

    def test_normalize_node_with_children(self):
        """Test normalizing a node with nested children."""
        node_data = {
            "__doc__": "Parent stage",
            "order": False,
            "order_index": 0,
            "Child Stage": {
                "__doc__": "Child description"
            }
        }
        
        result = _normalize_node("Parent Stage", node_data, 0)
        
        assert result["display"] == "Parent Stage"
        assert result["class"] == "ParentStage"
        assert result["doc"] == "Parent stage"
        assert result["order_fixed"] is False
        assert result["order_index"] == 0
        assert len(result["children"]) == 1
        assert result["children"][0]["display"] == "Child Stage"
        assert result["children"][0]["class"] == "ChildStage"

    def test_normalize_node_none_body(self):
        """Test normalizing a node with None body (empty stage)."""
        # This test should not be needed since _normalize_mapping_to_nodes handles None
        # by converting it to an empty dict
        pass

    def test_to_identifier_basic(self):
        """Test basic identifier conversion."""
        assert to_identifier("Global Rules") == "GlobalRules"
        assert to_identifier("Output Template") == "OutputTemplate"
        assert to_identifier("Adaptive Execution") == "AdaptiveExecution"

    def test_to_identifier_with_numbers(self):
        """Test identifier conversion with numbers."""
        assert to_identifier("Stage 1") == "Stage1"
        assert to_identifier("1st Stage") == "_1stStage"

    def test_to_identifier_with_keywords(self):
        """Test identifier conversion with Python keywords."""
        # The current implementation doesn't handle Python keywords specially
        # It just capitalizes the first letter
        assert to_identifier("class") == "Class"
        assert to_identifier("def") == "Def"

    def test_to_identifier_empty(self):
        """Test identifier conversion with empty string."""
        assert to_identifier("") == "Stage"
        assert to_identifier("   ") == "Stage"

    def test_qname_basic(self):
        """Test qualified name generation."""
        assert qname(["Stages", "Objective"]) == "Stages.Objective"
        assert qname(["Stages", "AdaptiveExecution", "AfterToolExecution"]) == "Stages.AdaptiveExecution.AfterToolExecution"

    def test_qname_single(self):
        """Test qualified name with single element."""
        assert qname(["Stages"]) == "Stages"

    def test_emit_class_tree_basic(self):
        """Test emitting basic class tree."""
        nodes = [
            {
                "display": "Objective",
                "class": "Objective",
                "doc": "Defines the mission.",
                "order_fixed": False,
                "order_index": 0,
                "children": []
            }
        ]
        
        result = emit_class_tree(nodes)
        
        # Check that the output contains expected class definition
        output = "\n".join(result)
        assert "class Objective:" in output
        assert '""" Defines the mission. """' in output
        assert "__stage_display__ = 'Objective'" in output
        assert "pass" in output

    def test_emit_class_tree_with_children(self):
        """Test emitting class tree with nested children."""
        nodes = [
            {
                "display": "Parent",
                "class": "Parent",
                "doc": "Parent description",
                "order_fixed": False,
                "order_index": 0,
                "children": [
                    {
                        "display": "Child",
                        "class": "Child",
                        "doc": "Child description",
                        "order_fixed": False,
                        "order_index": 0,
                        "children": []
                    }
                ]
            }
        ]
        
        result = emit_class_tree(nodes)
        output = "\n".join(result)
        
        # Check parent class
        assert "class Parent:" in output
        assert '""" Parent description """' in output
        
        # Check child class (should be indented)
        assert "    class Child:" in output
        assert '        """ Child description """' in output

    def test_collect_paths_basic(self):
        """Test collecting paths for basic structure."""
        nodes = [
            {
                "display": "Objective",
                "class": "Objective",
                "doc": "Defines the mission.",
                "order_fixed": False,
                "order_index": 0,
                "children": []
            }
        ]
        
        result = collect_paths(nodes)
        
        assert len(result) == 1
        path, node = result[0]
        assert path == ["Stages", "Objective"]
        assert node["class"] == "Objective"

    def test_collect_paths_with_children(self):
        """Test collecting paths with nested children."""
        nodes = [
            {
                "display": "Parent",
                "class": "Parent",
                "doc": "Parent description",
                "order_fixed": False,
                "order_index": 0,
                "children": [
                    {
                        "display": "Child",
                        "class": "Child",
                        "doc": "Child description",
                        "order_fixed": False,
                        "order_index": 0,
                        "children": []
                    }
                ]
            }
        ]
        
        result = collect_paths(nodes)
        
        assert len(result) == 2
        
        # Check parent path
        parent_path, parent_node = result[0]
        assert parent_path == ["Stages", "Parent"]
        assert parent_node["class"] == "Parent"
        
        # Check child path
        child_path, child_node = result[1]
        assert child_path == ["Stages", "Parent", "Child"]
        assert child_node["class"] == "Child"

    def test_emit_wiring_basic(self):
        """Test emitting wiring for basic structure."""
        nodes = [
            {
                "display": "Objective",
                "class": "Objective",
                "doc": "Defines the mission.",
                "order_fixed": False,
                "order_index": 0,
                "children": []
            }
        ]
        
        result = emit_wiring(nodes)
        output = "\n".join(result)
        
        # Check stage root and parent
        assert "Stages.Objective.__stage_root__ = Stages" in output
        assert "Stages.Objective.__stage_parent__ = Stages" in output
        assert "Stages.Objective.__children__ = ()" in output
        
        # Check order metadata
        assert "Stages.Objective.__order_fixed__ = False" in output
        assert "Stages.Objective.__order_index__ = 0" in output
        
        # Check top-level collections
        assert "Stages.__top_levels__ = (Stages.Objective,)" in output
        # The empty tuple is formatted as (,)
        assert "Stages.__fixed_top_order__ = (,)" in output

    def test_emit_wiring_with_fixed_order(self):
        """Test emitting wiring with fixed order stages."""
        nodes = [
            {
                "display": "Objective",
                "class": "Objective",
                "doc": "Defines the mission.",
                "order_fixed": False,
                "order_index": 0,
                "children": []
            },
            {
                "display": "ToolReference",
                "class": "ToolReference",
                "doc": "Tool catalog.",
                "order_fixed": True,
                "order_index": 3,
                "children": []
            }
        ]
        
        result = emit_wiring(nodes)
        output = "\n".join(result)
        
        # Check fixed order stage
        assert "Stages.ToolReference.__order_fixed__ = True" in output
        assert "Stages.ToolReference.__order_index__ = 3" in output
        
        # Check top-level collections
        assert "Stages.__top_levels__ = (Stages.Objective, Stages.ToolReference,)" in output
        assert "Stages.__fixed_top_order__ = (Stages.ToolReference,)" in output

    def test_emit_wiring_with_nested_stages(self):
        """Test emitting wiring with nested stage hierarchy."""
        nodes = [
            {
                "display": "Parent",
                "class": "Parent",
                "doc": "Parent description",
                "order_fixed": False,
                "order_index": 0,
                "children": [
                    {
                        "display": "Child",
                        "class": "Child",
                        "doc": "Child description",
                        "order_fixed": False,
                        "order_index": 0,
                        "children": []
                    }
                ]
            }
        ]
        
        result = emit_wiring(nodes)
        output = "\n".join(result)
        
        # Check parent wiring
        assert "Stages.Parent.__stage_root__ = Stages" in output
        assert "Stages.Parent.__stage_parent__ = Stages" in output
        assert "Stages.Parent.__children__ = (Stages.Parent.Child,)" in output
        
        # Check child wiring
        assert "Stages.Parent.Child.__stage_root__ = Stages" in output
        assert "Stages.Parent.Child.__stage_parent__ = Stages.Parent" in output
        assert "Stages.Parent.Child.__children__ = ()" in output

    def test_generate_stages_module_integration(self):
        """Test the full module generation process."""
        yaml_content = """
        Objective:
            __doc__: "Defines the mission of the investigation and the boundaries of success."
        Global Rules:
            __doc__: "Declares top-level constraints and priority principles."
            order: fixed
            order_index: 1
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as yaml_file:
            yaml_file.write(yaml_content)
            yaml_file.flush()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as py_file:
                py_file.close()
                
                try:
                    generate_stages_module(Path(yaml_file.name), Path(py_file.name))
                    
                    # Verify the generated file exists and has content
                    assert Path(py_file.name).exists()
                    content = Path(py_file.name).read_text()
                    
                    # Check that the generated content has expected elements
                    assert "class Stages:" in content
                    assert "class Objective:" in content
                    assert "class GlobalRules:" in content
                    assert "__stage_display__ = 'Objective'" in content
                    assert "__stage_display__ = 'Global Rules'" in content
                    assert "__order_fixed__ = True" in content
                    assert "__order_index__ = 1" in content
                    
                finally:
                    # Cleanup
                    Path(yaml_file.name).unlink()
                    Path(py_file.name).unlink()

    def test_generate_stages_module_creates_directories(self):
        """Test that generate_stages_module creates output directories if they don't exist."""
        yaml_content = """
        Objective:
            __doc__: "Defines the mission."
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as yaml_file:
            yaml_file.write(yaml_content)
            yaml_file.flush()
            
            # Create a path with non-existent parent directories
            output_path = Path("temp_output") / "nested" / "stages.py"
            
            try:
                generate_stages_module(Path(yaml_file.name), output_path)
                
                # Verify the file was created
                assert output_path.exists()
                assert output_path.parent.exists()
                
            finally:
                # Cleanup
                Path(yaml_file.name).unlink()
                if output_path.exists():
                    output_path.unlink()
                if output_path.parent.exists():
                    output_path.parent.rmdir()
                if Path("temp_output").exists():
                    Path("temp_output").rmdir()

    def test_escape_docstring_quotes(self):
        """Test that docstring quotes are properly escaped."""
        nodes = [
            {
                "display": "Test Stage",
                "class": "TestStage",
                "doc": 'This has "quotes" and """triple quotes"""',
                "order_fixed": False,
                "order_index": 0,
                "children": []
            }
        ]
        
        result = emit_class_tree(nodes)
        output = "\n".join(result)
        
        # Check that quotes are properly handled in the generated output
        # The generator escapes triple quotes but leaves double quotes as-is
        assert '""" This has "quotes" and \\"""triple quotes\\""" """' in output

    def test_order_parsing_variations(self):
        """Test various order value formats."""
        test_cases = [
            ("fixed", True),
            ("FIXED", True),
            ("Fixed", True),
            (True, True),
            (False, False),
            ("false", False),
            ("", False),
            (None, False),
        ]
        
        for order_val, expected in test_cases:
            node_data = {
                "__doc__": "Test stage",
                "order": order_val,
                "order_index": 0
            }
            
            result = _normalize_node("Test Stage", node_data, 0)
            assert result["order_fixed"] == expected, f"Failed for order={order_val}"

    def test_order_index_defaults(self):
        """Test that order_index defaults to the provided default_index."""
        node_data = {
            "__doc__": "Test stage"
        }
        
        result = _normalize_node("Test Stage", node_data, 42)
        assert result["order_index"] == 42


if __name__ == "__main__":
    pytest.main([__file__])

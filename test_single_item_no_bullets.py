#!/usr/bin/env python3
"""
Test script to validate the new single-item no-bullets behavior.
This can be run independently to verify the changes work correctly.
"""

from src.structured_prompt import StructuredPromptFactory, PromptSection
from tests.stubs.prompt_structure import Stages


def test_single_item_no_bullets():
    """Test that single items don't get bullets but maintain indentation."""
    prompt = StructuredPromptFactory(stage_root=Stages)
    prompt[Stages.Objective] = ["Single item only"]

    rendered = prompt.render_prompt()
    print("=== SINGLE ITEM TEST ===")
    print(rendered)

    # Verify single item has no bullet but proper indentation
    lines = rendered.strip().split('\n')
    objective_content_line = None
    for line in lines:
        if "Single item only" in line:
            objective_content_line = line
            break

    assert objective_content_line is not None, "Content line not found"

    # Should start with indentation but no bullet
    stripped = objective_content_line.lstrip()
    leading_spaces = len(objective_content_line) - len(stripped)

    assert leading_spaces > 0, "Should have indentation"
    assert not stripped.startswith('-'), "Should not start with dash bullet"
    assert not stripped.startswith('*'), "Should not start with asterisk bullet"
    assert not stripped[0].isdigit(), "Should not start with number bullet"
    assert stripped == "Single item only", "Content should be plain text"
    print("✓ Single item correctly rendered without bullet")


def test_multiple_items_have_bullets():
    """Test that multiple items still get bullets."""
    prompt = StructuredPromptFactory(stage_root=Stages)
    prompt[Stages.Objective] = ["First item", "Second item"]

    rendered = prompt.render_prompt()
    print("\n=== MULTIPLE ITEMS TEST ===")
    print(rendered)

    # Both items should have bullets
    assert "- First item" in rendered, "First item should have bullet"
    assert "- Second item" in rendered, "Second item should have bullet"
    print("✓ Multiple items correctly rendered with bullets")


def test_nested_single_items():
    """Test nested sections with single items."""
    prompt = StructuredPromptFactory(stage_root=Stages)
    prompt[Stages.Planning] = [
        PromptSection("Single Item Section", items=["Only one item"]),
        PromptSection("Multi Item Section", items=["Item A", "Item B"])
    ]

    rendered = prompt.render_prompt()
    print("\n=== NESTED SINGLE/MULTI TEST ===")
    print(rendered)

    # The single item section should not have bullets for its item
    lines = rendered.split('\n')
    found_single_content = False
    found_multi_content = False

    for i, line in enumerate(lines):
        if "Only one item" in line:
            # Should not have bullet
            stripped = line.lstrip()
            assert not stripped.startswith('-'), f"Single item should not have bullet: {line}"
            assert not stripped.startswith('*'), f"Single item should not have bullet: {line}"
            found_single_content = True
        elif "Item A" in line or "Item B" in line:
            # Should have bullet
            assert "* Item A" in line or "* Item B" in line, f"Multi items should have bullets: {line}"
            found_multi_content = True

    assert found_single_content, "Single item content not found"
    assert found_multi_content, "Multi item content not found"
    print("✓ Nested sections correctly handle single vs multiple items")


def test_bullet_style_none_overrides():
    """Test that bullet_style=None still overrides single item behavior."""
    prompt = StructuredPromptFactory(stage_root=Stages)

    # Single item with explicit bullet_style=None should still have no bullet
    prompt[Stages.ToolReference] = PromptSection(
        bullet_style=None,
        items=["Single item with explicit None"]
    )

    rendered = prompt.render_prompt()
    print("\n=== BULLET_STYLE=None OVERRIDE TEST ===")
    print(rendered)

    # Should have no bullet (same as before)
    assert "Single item with explicit None" in rendered
    lines = rendered.split('\n')
    content_line = None
    for line in lines:
        if "Single item with explicit None" in line:
            content_line = line
            break

    assert content_line is not None
    stripped = content_line.lstrip()
    assert not stripped.startswith('-'), "Should not have bullet with explicit None"
    assert not stripped.startswith('*'), "Should not have bullet with explicit None"
    print("✓ bullet_style=None correctly overrides single item behavior")


def test_appending_to_single_item_adds_bullets():
    """Test that appending to a single item adds bullets to both."""
    prompt = StructuredPromptFactory(stage_root=Stages)

    # Start with single item (no bullet)
    prompt[Stages.Planning] = ["First step"]
    rendered1 = prompt.render_prompt()
    print("\n=== BEFORE APPENDING (SINGLE ITEM) ===")
    print(rendered1)

    # Should not have bullet
    assert "First step" in rendered1
    assert "- First step" not in rendered1, "Single item should not have bullet initially"

    # Append another item (should add bullets to both)
    prompt[Stages.Planning] = ["Second step"]
    rendered2 = prompt.render_prompt()
    print("\n=== AFTER APPENDING (MULTIPLE ITEMS) ===")
    print(rendered2)

    # Now both should have bullets
    assert "- First step" in rendered2, "First item should now have bullet"
    assert "- Second step" in rendered2, "Second item should have bullet"
    print("✓ Appending to single item correctly adds bullets to both items")


if __name__ == "__main__":
    test_single_item_no_bullets()
    test_multiple_items_have_bullets()
    test_nested_single_items()
    test_bullet_style_none_overrides()
    test_appending_to_single_item_adds_bullets()
    print("\n🎉 All tests passed! Single-item no-bullets behavior is working correctly.")
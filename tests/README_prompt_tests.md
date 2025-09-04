# Prompt Infrastructure Tests

This directory contains comprehensive tests for the prompt infrastructure system, covering all the acceptance examples and design principles outlined in the documentation.

## Test Files

### `test_dynamic_prompt_builder.py`
The main test suite covering all aspects of the dynamic prompt builder:

- **Core Functionality Tests** (1-10): Cover all acceptance examples from the documentation
- **Configuration Tests**: Test indentation preferences and formatting options
- **Edge Cases**: Test empty prompts, prologue-only prompts, etc.
- **Complex Scenarios**: Test nested structures and arbitrary stage names

## Running the Tests

### Prerequisites
```bash
pip install pytest
```

### Method 1: Using pytest directly
```bash
# From the project root
PYTHONPATH=src python3 -m pytest tests/test_dynamic_prompt_builder.py -v

# From the tests directory
cd tests
PYTHONPATH=../src python3 -m pytest test_dynamic_prompt_builder.py -v
```

### Method 2: Using the test runner script
```bash
# From the project root
python3 tests/run_prompt_tests.py

# From the tests directory
cd tests
python3 run_prompt_tests.py
```

## Test Coverage

The tests cover all the key principles from the acceptance examples:

### 1. Append vs Replace Semantics
- **Append**: Assigning lists appends items to sections
- **Replace**: Assigning `PromptSection` objects replaces sections

### 2. Hierarchical Addressing
- Direct deep stage references auto-create ancestors
- Two-step addressing works equivalently

### 3. Content Types
- Plain strings
- `PromptText` objects
- `PromptSection` objects with nested content
- Mixed content types

### 4. Formatting Control
- Custom indentation preferences
- Bullet style control
- Blank line preferences

### 5. Special Features
- Critical steps (root and section level)
- Prologue text
- Stage root inheritance

## Test Structure

Each test follows this pattern:
1. **Setup**: Create prompt and add content
2. **Action**: Perform the operation being tested
3. **Verification**: Check the rendered output matches expectations

## Example Test

```python
def test_append_when_setting_array_value(self):
    """Test that assigning a List[ItemLike] to a section appends items."""
    prompt = DigmaStructuredPrompt()
    
    # First assignment
    prompt[Stages.AdaptiveExecution] = [
        PromptSection(
            name=Stages.AdaptiveExecution.AdaptiveExecutionRule,
            subtitle="Follow your planned steps in order, but you MAY:",
            items=["Insert new tool calls if new evidence suggests they will help meet the objective."]
        ),
    ]
    
    # Appending more content to the same section key
    prompt[Stages.AdaptiveExecution] = [
        "Do not repeat steps already done."
    ]
    
    rendered = prompt.render_prompt()
    
    # Verify both sets of content are present
    assert "Insert new tool calls if new evidence suggests they will help meet the objective." in rendered
    assert "Do not repeat steps already done." in rendered
```

## Troubleshooting

### Import Errors
If you get import errors, make sure the `PYTHONPATH` includes the `src` directory:
```bash
export PYTHONPATH=src:$PYTHONPATH
```

### Test Failures
If tests fail, check:
1. The actual rendered output vs. expected output
2. Stage names and hierarchy (they may be humanized differently)
3. Indentation and bullet progression (may vary based on configuration)

### Running Individual Tests
To run a specific test:
```bash
PYTHONPATH=src python3 -m pytest tests/test_dynamic_prompt_builder.py::TestDynamicPromptBuilder::test_name -v
```

## Contributing

When adding new tests:
1. Follow the existing naming convention
2. Include clear docstrings explaining what's being tested
3. Test both the happy path and edge cases
4. Verify the test passes before committing

## Related Documentation

- `docs/prompt_framework/prompt_infra_acceptance_examples.md` - Acceptance examples
- `docs/prompt_framework/prompt_infra_design.md` - Design principles
- `src/dynamic_prompt/dynamic_prompt_builder.py` - Implementation

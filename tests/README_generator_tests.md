# Prompt Stages Generator Tests

This directory contains comprehensive tests for the prompt stages generator and integration tests that validate the generated stages work correctly with the prompt infrastructure.

## Test Files

### 1. `test_prompt_stages_generator.py`
**Unit tests for the generator itself** - Tests all the internal functions and logic of the prompt stages generator.

**What it tests:**
- YAML parsing and validation
- Node normalization and structure building
- Identifier conversion (e.g., "Global Rules" → "GlobalRules")
- Class tree generation
- Metadata wiring (parent/child relationships, ordering)
- Full module generation process
- Edge cases and error handling

**Key test categories:**
- `test_load_yaml_*` - YAML file loading and validation
- `test_normalize_*` - Data structure normalization
- `test_to_identifier_*` - Identifier conversion rules
- `test_emit_*` - Code generation functions
- `test_generate_stages_module_*` - End-to-end generation

### 2. `test_generated_stages_integration.py`
**Integration tests** - Tests that the generated stages work correctly with the prompt infrastructure, implementing all the acceptance examples from the documentation.

**What it tests:**
- All 10 acceptance examples from `prompt_infra_acceptance_examples.md`
- Generated stages structure and metadata integrity
- Fixed ordering functionality
- Custom indentation preferences
- Arbitrary child addition

**Key test categories:**
- `test_acceptance_example_*` - Each of the 10 documented examples
- `test_generated_stages_structure` - Basic structure validation
- `test_generated_stages_metadata_integrity` - Metadata completeness
- `test_generated_stages_ordering_integrity` - Fixed ordering validation
- `test_generated_stages_with_custom_indentation` - Custom preferences
- `test_generated_stages_arbitrary_children` - Dynamic child addition

## Running the Tests

### Option 1: Run All Generator Tests
```bash
# From the project root
python3 tests/run_generator_tests.py

# Or with PYTHONPATH set
PYTHONPATH=src python3 tests/run_generator_tests.py
```

### Option 2: Run Specific Test Files
```bash
# Run only generator unit tests
python3 tests/run_generator_tests.py test_prompt_stages_generator.py

# Run only integration tests
python3 tests/run_generator_tests.py test_generated_stages_integration.py

# Or run directly with pytest
PYTHONPATH=src python3 -m pytest tests/test_prompt_stages_generator.py -v
PYTHONPATH=src python3 -m pytest tests/test_generated_stages_integration.py -v
```

### Option 3: Run with pytest directly
```bash
# From the project root
PYTHONPATH=src python3 -m pytest tests/test_prompt_stages_generator.py -v
PYTHONPATH=src python3 -m pytest tests/test_generated_stages_integration.py -v

# Run all tests in the tests directory
PYTHONPATH=src python3 -m pytest tests/ -v
```

## Test Coverage

### Generator Unit Tests (25 tests)
- **YAML Processing**: Loading, validation, error handling
- **Data Normalization**: Structure building, metadata extraction
- **Code Generation**: Class tree emission, metadata wiring
- **Edge Cases**: Empty stages, special characters, Python keywords
- **Integration**: Full module generation workflow

### Integration Tests (15 tests)
- **Acceptance Examples**: All 10 documented use cases
- **Structure Validation**: Generated class hierarchy and metadata
- **Functionality**: Fixed ordering, custom preferences, dynamic content
- **Real-world Usage**: Complex nested structures and mixed content types

## What the Tests Validate

### 1. Generator Correctness
- YAML → Python class conversion is accurate
- Metadata (parent/child relationships, ordering) is correctly wired
- Generated code follows Python syntax rules
- Error handling works for invalid inputs

### 2. Generated Stages Integrity
- All stages have complete metadata (`__stage_root__`, `__stage_parent__`, etc.)
- Fixed ordering is properly implemented
- Display names are correctly set
- Parent-child relationships are accurate

### 3. Prompt Infrastructure Compatibility
- Generated stages work seamlessly with `StructuredPromptFactory`
- All acceptance examples render correctly
- Fixed ordering is respected during rendering
- Custom indentation preferences work with generated stages

### 4. Real-world Usage Scenarios
- Complex nested stage hierarchies
- Mixed content types (strings, PromptSection, PromptText)
- Dynamic content addition
- Custom formatting and styling

## Test Data

The integration tests use a minimal test YAML that covers:
- **Top-level stages**: Objective, Global Rules, Operating Principles, ToolReference (fixed order), Scoping, Planning, AdaptiveExecution, Output, QualityGates
- **Nested stages**: AdaptiveExecution.AdaptiveExecutionRule, BeforeToolExecution, AfterToolExecution, Output.OutputTemplate, Output.OutputTemplateRules
- **Fixed ordering**: ToolReference with `order: fixed` and `order_index: 3`

This provides comprehensive coverage while keeping test execution fast.

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `PYTHONPATH=src` is set or run from the project root
2. **Missing Dependencies**: Install `pytest` and `pyyaml` if not already installed
3. **Path Issues**: The tests create temporary files - ensure write permissions in the tests directory

### Debug Mode
Run tests with verbose output to see exactly what's happening:
```bash
PYTHONPATH=src python3 -m pytest tests/test_prompt_stages_generator.py -v -s
```

### Test Isolation
Each test method has its own setup/teardown to ensure tests don't interfere with each other.

## Related Documentation

- **Generator Specs**: `docs/prompt_framework/generator/generator_specs.md`
- **Acceptance Examples**: `docs/prompt_framework/builder/prompt_infra_acceptance_examples.md`
- **Design Principles**: `docs/prompt_framework/prompt_infra_design.md`

## Adding New Tests

### For Generator Unit Tests
Add new test methods to `TestPromptStagesGenerator` class:
- Test specific edge cases or error conditions
- Test new generator features
- Test performance with large inputs

### For Integration Tests
Add new test methods to `TestGeneratedStagesIntegration` class:
- Test new acceptance examples
- Test new prompt infrastructure features
- Test complex real-world scenarios

### Test Naming Convention
- Unit tests: `test_<function_name>_<scenario>`
- Integration tests: `test_<feature>_<scenario>`
- Acceptance tests: `test_acceptance_example_<number>_<description>`

## Performance Notes

- **Unit tests**: Fast execution (< 1 second)
- **Integration tests**: Moderate execution (2-5 seconds due to file I/O and module generation)
- **Full test suite**: Complete in under 10 seconds

The tests are designed to be fast enough for development workflow while providing comprehensive coverage.

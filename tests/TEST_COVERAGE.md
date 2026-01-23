# Test Coverage Summary

This document outlines the test coverage for gitree CLI arguments shown in `gt -h`.

## Test Structure

### 1. General Options Tests (`test_general_options.py`)
Tests for general CLI flags:
- ✅ `test_no_arg` - Default behavior (no arguments)
- ✅ `test_version` - Version display (`--version`)
- ✅ `test_help` - Help display (`--help`)
- ✅ `test_verbose` - Verbose logging (`--verbose`)
- ✅ `test_no_config` - Config override (`--no-config`)

**Not Tested:**
- `--config-user` - Requires GUI/editor interaction

### 2. Semantic Flags Tests (`test_semantic_options.py`)
Tests for quick action semantic flags:
- ✅ `test_full` - Full tree display (`--full`)
- ✅ `test_emoji` - Emoji output (`--emoji`)
- ✅ `test_copy` - Copy to clipboard (`--copy`)
- ✅ `test_combined_semantic_flags` - Multiple flags together (`--full --emoji`)

**Not Tested:**
- `-i, --interactive` - Requires user input/interaction
- `--only-types` - Complex argument parsing (can be added later)

### 3. Positional Arguments Tests (`test_positional_args.py`)
Tests for PATH arguments:
- ✅ `test_default_path` - Default to current directory
- ✅ `test_single_path` - Single directory path
- ✅ `test_multiple_paths` - Multiple directory paths
- ✅ `test_file_pattern_python` - File pattern support
- ✅ `test_specific_directory_path` - Specific subdirectory

## Test Philosophy

### What We Test
- Long-form flags only (e.g., `--version` not `-v`)
- Non-interactive functionality
- Core features shown in `gt -h`

### What We Don't Test
- Short-form aliases (assumed to work if long-form works)
- Interactive modes that require user input
- GUI-related features (`--config-user`)
- Complex edge cases with glob patterns

## Running Tests

```bash
# Run all tests
python -m tests

# Run specific test file
python -m unittest tests.test_general_options
python -m unittest tests.test_semantic_options
python -m unittest tests.test_positional_args
```

## Test Results
All 14 tests passing ✅

## Future Additions
- Add `--only-types` test when argument parsing is more stable
- Add more complex path pattern tests if needed
- Consider mock-based tests for interactive features

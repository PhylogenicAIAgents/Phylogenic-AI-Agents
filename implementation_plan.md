# Implementation Plan

## Overview
Address 54 failing tests across 7 component categories by fixing configuration mismatches, parameter inconsistencies, and test fixture issues in the Allele codebase. The primary focus is restoring functionality to the evolution engine, LLM clients, memory tests, benchmark scaling, ML analytics, and core LNN edge case handling through targeted fixes to parameter signatures, configuration loading, assertion tolerances, and fixture compatibility.

## Types
### LLMConfig Updates
New configuration handling for OpenAI and Ollama clients with proper API key validation and fallback mechanisms. Add optional api_key parameter to constructor signatures to prevent TypeError during initialization.

### Evolution Fitness Function
Modify generate_fitness_function in test utilities to accept optional seed parameter matching expected EvolutionaryAlgorithm API signatures used in mutation and elitism tests.

### Memory Test Assertions
Update floating-point precision assertions in memory cleanup tests to use tolerances instead of exact equality comparisons for garbage collection verification.

## Files
### New files to be created
- `src/allele/llm_config.py`: Centralized LLM configuration management with validation
- `scripts/fix_test_fixtures.py`: Automated script to update test fixtures for compatibility

### Existing files to be modified
- `src/allele/evolution.py`: Update fitness function generation signature (lines ~142-150)
- `src/allele/llm_openai.py`: Add optional api_key parameter to LLMConfig constructor (line ~87)
- `src/allele/llm_ollama.py`: Add optional api_key parameter to LLMConfig constructor
- `tests/bench/test_kraken_memory.py`: Update memory cleanup assertion tolerance (line ~157)
- `tests/unit/test_ml_analytics_component.py`: Add configuration fallback loading
- `tests/bench/test_kraken_scaling.py`: Fix pytest-benchmark fixture conflicts
- `tests/unit/test_kraken_edgecases.py`: Update input validation for sequence bounds

### Files to be deleted or moved
- None required

### Configuration file updates
- `pyproject.toml`: Add test dependency compatibility settings
- `.env.example`: Document optional LLM API key configuration

## Functions
### New functions
- `src/allele/llm_config.py::validate_llm_config()`: Validation function for LLM configurations with environment variable fallbacks
- `tests/test_utils.py::generate_fitness_function_with_seed()`: Enhanced fitness function generator with seed support

### Modified functions
- `src/allele/evolution.py::GeneticOperators.mutate()`: Update parameter signature for seed handling
- `src/allele/llm_client.py::LLMConfig.__init__()`: Make api_key parameter optional with validation
- `tests/bench/test_kraken_memory.py::test_memory_cleanup_after_processing()`: Add tolerance to memory assertion
- `tests/conftest.py::fitness_function()`: Update signature to match generate_fitness_function call

### Removed functions
- None required for migration strategy

## Classes
### New classes
- `src/allele/llm_config.py::LLMConfigValidator`: Validation class for LLM configuration management
- `tests/fixtures.py::BenchmarkFixture`: Custom pytest fixtures for benchmark compatibility

### Modified classes
- `src/allele/llm_client.py::LLMConfig`: Add optional api_key parameter with property validation
- `tests/bench/test_kraken_memory.py::TestKrakenMemoryBenchmarks`: Update assertion methods for floating-point tolerance

### Removed classes
- None required for replacement strategy

## Dependencies
### New packages
- `pytest-benchmark>=4.0.0`: Fixed version for benchmark fixture compatibility
- `tiktoken>=0.5.0`: Enhanced token estimation for LLM clients

### Version changes
- Update `openai` to `>=1.0.0` for API compatibility
- Update `numpy` to `>=1.24.0` for random state handling

### Integration requirements
- Environment variable configuration for optional LLM API keys
- pytest fixture updates for benchmark scaling tests

## Testing
### Test file requirements
- `tests/test_config_validation.py`: New test file for LLM configuration validation
- `tests/test_memory_assertions.py`: Tests for memory cleanup tolerance
- `tests/test_fitness_function.py`: Tests for fitness function signature compatibility

### Existing test modifications
- `tests/unit/test_evolution_mutation_and_elitism.py`: Update fixture calls for seed parameter
- `tests/unit/test_llm_openai_*.py`: Update configuration initialization calls
- `tests/unit/test_ollama_client.py`: Remove required api_key from setup fixtures

### Validation strategies
- Regression testing for all 54 previously failing tests
- Compatibility testing across Python 3.10-3.12
- Memory usage validation for fixed benchmark tests

## Implementation Order
1. Fix evolution engine fitness function signature to accept seed parameter
2. Update LLM configuration classes to make api_key optional with validation
3. Fix memory test floating-point assertion tolerance
4. Resolve benchmark scaling test fixture conflicts
5. Add ML analytics configuration fallbacks
6. Update core LNN edge case input validation
7. Run full test suite validation and regression testing

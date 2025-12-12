# GitHub Actions Workflows for Allele SDK

This directory contains comprehensive CI/CD workflows that focus on **API contract testing** and **functionality testing** to ensure the quality and reliability of the Allele SDK.

## 🚀 Workflow Overview

### [`api-contract-testing.yml`](api-contract-testing.yml) - API Contract Testing
**Primary Focus:** OpenAPI specifications validation and client generation testing

**Triggers:**
- Push to `main` or `feature/**` branches with API spec changes
- PR targeting `main` with API specification changes

**Key Jobs:**
- ✅ **OpenAPI Specification Validation** - Lint all 5 API specs with Redocly CLI
- ✅ **Client SDK Generation Testing** - Generate Python/TypeScript/Go clients
- ✅ **API Contract Diff Analysis** - Analyze breaking changes in PRs
- ✅ **PR Commenting** - Automated documentation links and validation status
- ✅ **GitHub Actions Validation** - Ensure workflow files are valid YAML

### [`functionality-testing.yml`](functionality-testing.yml) - Functionality Testing Suite
**Primary Focus:** Core SDK functionality, performance, and integration testing

**Triggers:**
- Push to any branch (excluding docs-only changes)
- PR targeting `main` (excluding API spec changes)

**Key Jobs:**
- ✅ **Unit Tests** - Comprehensive coverage with pytest (Python 3.11, 3.12)
- ✅ **Integration Tests** - End-to-end testing with Redis dependency
- ✅ **Agent Lifecycle Tests** - Core agent initialization and chat functionality
- ✅ **Genome Operations Tests** - Trait manipulation and serialization
- ✅ **Evolution Engine Tests** - Genetic algorithm simulation
- ✅ **Performance Benchmarks** - Speed and efficiency measurements
- ✅ **Code Quality** - Pre-commit hooks, mypy, ruff linting
- ✅ **Security Scanning** - Dependency vulnerability checks with Bandit
- ✅ **LLM Integration Tests** - Controlled provider testing (opt-in via labels)
- ✅ **Deployment Preview** - Build verification and staging readiness

## 🎯 Workflow Philosophy

### API-First Development
- **Contract Validation:** All API specifications must be valid OpenAPI 3.1
- **Client Generation:** Specifications must generate working client SDKs
- **Breaking Changes:** Automatic detection of contract modifications

### Functionality Quality Gates
- **85%+ Test Coverage** requirement for unit tests
- **Cross-Python Support** (3.11 and 3.12)
- **Integration Testing** with real dependencies
- **Performance Regression** detection
- **Security Vulnerability** scanning

### Developer Experience
- **Fast Feedback Loops** with parallel job execution
- **Rich PR Comments** with test results and deployment status
- **Artifact Uploads** for debugging and analysis
- **Opt-in Advanced Testing** via PR labels

## 📋 How to Use

### For All PRs
```bash
# Standard workflow triggers automatically
# - API contract testing for docs/api/ changes
# - Functionality testing for src/ changes
```

### For API Specification Changes
1. Modify `.yaml` files in `docs/api/`
2. Push to feature branch
3. **API Contract Testing** workflow runs automatically
4. Check PR comments for validation results

### For Functionality Changes
1. Modify code in `src/allele/`
2. Push to feature branch
3. **Functionality Testing Suite** workflow runs automatically
4. All quality gates must pass for merge

### Advanced LLM Testing (Requires Label)
```bash
# Add 'test-llm' label to PR to trigger LLM integration tests
# Requires OPENAI_API_KEY secret to be set in repository settings
```

## 🔧 Workflow Configuration

### Required Secrets
```yaml
# Repository Settings > Secrets and Variables > Actions
OPENAI_API_KEY: sk-...  # For LLM integration tests (optional)
```

### Branch Protection Rules
```yaml
# Repository Settings > Branches > Branch Protection Rules
# For 'main' branch:
- Require PRs before merging
- Require status checks to pass:
  - validate-openapi-specs
  - unit-tests (Python 3.11)
  - unit-tests (Python 3.12)
  - linter-quality-checks
  - security-scan
- Require up-to-date branches before merging
```

### Custom Workflow Dispatch
```bash
# Manual trigger (for testing workflows)
gh workflow run "functionality-testing.yml" --ref feature-branch
```

## 📊 Workflow Jobs Breakdown

### API Contract Testing Pipeline
```
validate-openapi-specs → test-openapi-generator → contract-diff-check
                                   ↓
                         github-actions-lint
```

### Functionality Testing Pipeline
```
unit-tests ──────────────────┐
                            │
integration-tests ──────────┼─→ deploy-preview
                            │
agent-lifecycle-tests ──────┘
genome-operation-tests ──────┐
                             │
evolution-simulation-tests ──┼─→ (independent)
                             │
performance-benchmarks ──────┘
linter-quality-checks ──────┐
                             │
security-scan ───────────────┼─→ (quality gates)
                             │
llm-integration-tests ──────┘ (opt-in via label)
```

## 🎯 Test Categories

### Unit Tests (`tests/test_*.py`)
- Individual function/component testing
- Mock external dependencies
- Fast execution (<5 minutes)
- Coverage requirement: 85%+

### Integration Tests (`tests/*integration*.py`)
- Multi-component interaction
- Real Redis dependency
- Network calls (controlled)
- Test service orchestration

### Functionality Tests (Workflow Embedded)
- Agent lifecycle verification
- Genome operations validation
- Evolution engine simulation
- Performance benchmarking
- Security vulnerability scanning

### API Contract Tests
- OpenAPI specification validation
- Client SDK generation verification
- Breaking change detection
- Documentation accuracy

## 🚨 Handling Failures

### Common API Contract Failures
```bash
# Fix OpenAPI validation errors
npm install -g @redocly/cli
redocly lint docs/api/agent.yaml

# Fix client generation issues
# Check schema references and required fields
# Ensure examples match schema definitions
```

### Common Functionality Failures
```bash
# Fix unit test failures
pytest tests/ -v --tb=long

# Fix linting issues
pre-commit run --all-files

# Fix security issues
bandit -r src/allele/
```

### Debugging Workflows
```bash
# Check workflow run details in GitHub Actions tab
# Download artifacts for logs and reports
# Use local testing before pushing
```

## 📈 Metrics & Reporting

### Code Coverage
- **Target:** 85% minimum
- **Reported to:** Codecov
- **Failure threshold:** Below 80%

### Performance Benchmarks
- **Stored as artifacts** for regression tracking
- **30-day retention** for trend analysis
- **Required review** for significant regressions

### Security Reports
- **Vulnerability scans** on every push
- **SARIF format** integration with GitHub Security tab
- **30-day report retention** for compliance

## 🔗 Integration Points

### External Tool Integration
- **Codecov:** Coverage reporting and PR comments
- **SARIF:** Security vulnerability ingestion
- **Redocly:** API documentation generation
- **OpenAPI Generator:** Multi-language client SDKs

### PR Automation
- **Status Checks:** Required for branch protection
- **PR Comments:** Test results and deployment readiness
- **Artifact Links:** Download URLs for detailed reports

### Deployment Pipeline
- **Preview Environment:** Build verification for staging
- **Artifact Promotion:** Verified builds for production
- **Rollback Support:** Previous good versions available

## 🛠️ Development Workflow

### Local Testing Before Push
```bash
# Test API specs locally
npm install -g @redocly/cli
redocly lint docs/api/*.yaml

# Run unit tests locally
pytest tests/ --cov=src/allele

# Test build locally
python -m build
pip install -e .
```

### PR Strategy
1. **Feature Branch** → Push → Tests run
2. **Fix issues** → Push → Tests rerun
3. **Add 'test-llm' label** for advanced testing
4. **All checks pass** → Ready for review
5. **Required reviews** → Merge to main

### Continuous Integration
- **Fast feedback** on every push
- **Parallel execution** for quick results
- **Error reporting** directly in PR
- **Status badges** show build health

---

## 📚 Additional Resources

- [OpenAPI 3.1 Specification](https://spec.openapis.org/oas/v3.1.0)
- [Redocly CLI Documentation](https://redocly.com/docs/cli/)
- [OpenAPI Generator](https://openapi-generator.tech/)
- [Pytest Documentation](https://docs.pytest.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

**Need Help?** Check workflow logs in the Actions tab or create an issue! 🏃‍♂️

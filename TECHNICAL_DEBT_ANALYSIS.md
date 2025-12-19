# Technical Debt Analysis

## Critical Issues Found

### 🚨 **High Priority (Fix Immediately)**

#### 1. Multiple Artifact Directories
**Problem:** 5 separate artifact directories containing duplicate mypy logs
- `artifacts/` - 6 mypy logs (Python 3.9-3.14)
- `artifacts2/` - 1 mypy log (Python 3.9)
- `artifacts4/` - 6 mypy logs (Python 3.9-3.14)
- `artifacts5/` - 1 mypy log (Python 3.9)
- `artifacts6/` - 3 mypy logs (Python 3.9, 3.10, 3.14)

**Impact:** Repository bloat, confusion, wasted space

#### 2. Outdated Repository URLs
**Problem:** `pyproject.toml` contains old repository URLs
- Currently points to: `https://github.com/bravetto/allele`
- Should point to: `https://github.com/jimmyjdejesus-cmyk/Phylogenic-AI-Agents`

**Impact:** Broken links in package metadata

#### 3. GitHub Pages MkDocs Links
**Problem:** Current landing page still references old repo in documentation links
- Links point to: `https://github.com/allele-ai/allele`
- Should point to: `https://github.com/jimmyjdejesus-cmyk/Phylogenic-AI-Agents`

**Impact:** Broken navigation for users

### ⚠️ **Medium Priority (Fix Soon)**

#### 4. Package Naming Inconsistencies
**Problem:** Mixed references between "phylogenic" and "allele"
- Package name: "phylogenic"
- Some old references: "allele"
- PyPI package: "phylogenic"

**Impact:** User confusion, potential import issues

#### 5. Type Annotation Debt
**Problem:** Multiple mypy ignores in pyproject.toml
- `phylogenic.observability.*` - Temporarily ignored
- `phylogenic.llm_openai` - Missing imports ignored
- Tests excluded from type checking

**Impact:** Reduced code quality, potential bugs

### 📋 **Low Priority (Plan for Future)**

#### 6. Package Structure
**Current structure:** `src/phylogenic/` 
**Consider:** Moving to standard `src/` layout or `phylogenic/` at root

#### 7. Dependency Management
**Check:** All dependencies are up to date
**Review:** Optional dependencies grouping

## Recommended Actions

### Immediate (Fix Today)
1. **Consolidate artifacts** - Delete duplicate directories, keep only latest
2. **Update pyproject.toml URLs** - Fix repository links
3. **Update MkDocs configuration** - Fix GitHub links in documentation

### Short-term (This Week)
4. **Consistent naming** - Replace remaining "allele" references with "phylogenic"
5. **Type annotation cleanup** - Start addressing mypy ignores systematically

### Long-term (Next Sprint)
6. **Standardize package structure** - Evaluate src layout
7. **Dependency audit** - Review and update all packages
8. **Test coverage analysis** - Ensure all code paths are tested

## Estimated Effort
- **Immediate fixes:** 1-2 hours
- **Short-term fixes:** 4-6 hours  
- **Long-term improvements:** 1-2 weeks

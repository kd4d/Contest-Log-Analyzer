# Regression Test Data Management Strategy

**Date:** 2026-01-20  
**Status:** Discussion/Decision  
**Category:** Test Infrastructure

---

## Executive Summary

This document discusses best practices for managing test logs used in regression testing. The current approach stores test logs in `CONTEST_LOGS_REPORTS/Logs` (gitignored), but as test coverage expands, we need a strategy that ensures reproducibility, version control, and maintainability.

**Decision:** Move test logs to the test data git repository (`regression_baselines/Logs/`) for version control and co-location with test infrastructure.

---

## Current State Analysis

### Current Test Log Location

**Location:** `CONTEST_LOGS_REPORTS/Logs/` (gitignored in main repo)

**Structure:**
```
CONTEST_LOGS_REPORTS/Logs/
  2024/
    cq-ww-cw/
      k3lr.log
      w3lpl.log
      k1lz.log
    arrl-ss-cw/
      kd4d.log
      ...
  2025/
    ...
```

**References:**
- Web regression test script uses relative paths: `2024/cq-ww-cw/k3lr.log`
- Paths are relative to test data directory (via `TEST_DATA_DIR` environment variable)
- Test logs are used by web regression test suite

**Issues:**
- ❌ Not version controlled (gitignored)
- ❌ Not reproducible (different developers may have different logs)
- ❌ Can't track changes to test data
- ❌ Logs duplicated in ZIP archives (wasteful)
- ❌ Test data scattered (logs in one place, baselines in another)

---

## Best Practices Analysis

### Test Data Management Principles

**1. Version Control:**
- ✅ Test data should be version controlled for reproducibility
- ✅ Test data changes should be tracked (as tests are added/modified)
- ✅ Can rollback to specific test data versions
- ✅ Can see history of test data changes

**2. Reproducibility:**
- ✅ Same test data for all developers
- ✅ Same test data for CI/CD
- ✅ Can reproduce test results exactly
- ✅ Test data tied to specific test versions

**3. Co-location:**
- ✅ Test data should be co-located with test infrastructure
- ✅ Easier to manage (test data + baselines together)
- ✅ Clear separation from production/user data
- ✅ Single source of truth for test assets

**4. Separation of Concerns:**
- ✅ Test data separate from source code
- ✅ Test data separate from user data
- ✅ Test data separate from generated reports

**5. Size Management:**
- ✅ Test logs can be large (but manageable for local git repo)
- ✅ ZIP archives already contain logs (duplication)
- ✅ Local-only git repo avoids GitHub size limits

---

## Recommended Approach: Test Data in Test Repository

### Structure

**Test Data Repository:**
```
regression_baselines/              # Local git repo (never pushed)
  .git/                            # Git repository
  README.md                        # Test data documentation
  Logs/                            # Test logs (version controlled)
    2024/
      cq-ww-cw/
        k3lr.log
        w3lpl.log
        k1lz.log
      arrl-ss-cw/
        kd4d.log
        ...
    2025/
      ...
  web_baseline_v1.0.0-alpha.8/    # Baseline ZIP archives
    cq_ww_cw_3logs.zip
    ...
  web_baseline_v1.0.0-alpha.9/
    ...
```

**Benefits:**
- ✅ Test logs version controlled (can track changes)
- ✅ Co-located with baselines (single test repository)
- ✅ Reproducible (same logs for all developers)
- ✅ Can rollback test data versions
- ✅ Clear separation from production data
- ✅ Test data changes tracked in git history

### Path Updates Required

**Current Paths (web regression test):**
```python
'logs': ['2024/cq-ww-cw/k3lr.log', ...]
```

**Path Resolution:**
- Test logs resolved via `TEST_DATA_DIR` environment variable
- Default: `regression_baselines/Logs`
- Paths in test cases are relative to `TEST_DATA_DIR`

**Recommended:** Use environment variable for flexibility

---

## Alternative Approaches Considered

### Option 1: Keep Logs in Main Repo (Current)

**Structure:**
```
<main_repo>/
  CONTEST_LOGS_REPORTS/Logs/      # Gitignored
  regression_baselines/            # Separate repo
```

**Pros:**
- ✅ No path changes needed
- ✅ Easy access
- ✅ Familiar location

**Cons:**
- ❌ Not version controlled
- ❌ Not reproducible
- ❌ Can't track test data changes
- ❌ Test data scattered (logs vs baselines)
- ❌ Different developers may have different logs

**Verdict:** ❌ Not recommended - violates reproducibility principle

---

### Option 2: Test Data in Test Repository (Recommended)

**Structure:**
```
regression_baselines/              # Local git repo
  Logs/                            # Version controlled
  web_baseline_*/                  # Baseline archives
```

**Pros:**
- ✅ Version controlled
- ✅ Reproducible
- ✅ Co-located with baselines
- ✅ Can track test data changes
- ✅ Single test repository

**Cons:**
- ⚠️ Requires path updates in scripts
- ⚠️ Need to update environment variable handling

**Verdict:** ✅ **RECOMMENDED** - Best practice alignment

---

### Option 3: Git Submodule

**Structure:**
```
<main_repo>/
  test_data/                       # Git submodule
    Logs/
  regression_baselines/            # Separate repo
```

**Pros:**
- ✅ Version controlled
- ✅ Separate repository
- ✅ Can be shared across projects

**Cons:**
- ❌ Submodule management complexity
- ❌ More overhead (submodule updates, init, etc.)
- ❌ Overkill for local-only test data

**Verdict:** ❌ Not recommended - unnecessary complexity

---

### Option 4: Hybrid (Logs in Test Repo, Symlink in Main)

**Structure:**
```
regression_baselines/Logs/         # Actual location
<main_repo>/CONTEST_LOGS_REPORTS/Logs/  # Symlink
```

**Pros:**
- ✅ Version controlled (in test repo)
- ✅ Backward compatible paths
- ✅ Co-located with baselines

**Cons:**
- ❌ Symlink complexity (Windows vs Linux)
- ❌ Still need to manage test repo
- ❌ Confusing (two locations)

**Verdict:** ⚠️ Possible but adds complexity

---

## Implementation Plan

### Phase 1: Migrate Test Logs

**Steps:**
1. **Create Logs directory in test repo:**
   ```bash
   cd regression_baselines
   mkdir Logs
   ```

2. **Copy existing logs:**
   ```bash
   cp -r CONTEST_LOGS_REPORTS/Logs/* regression_baselines/Logs/
   ```

3. **Commit to test repo:**
   ```bash
   cd regression_baselines
   git add Logs/
   git commit -m "Add test logs for regression testing"
   ```

4. **Update .gitignore in main repo:**
   ```gitignore
   # Test logs moved to regression_baselines/Logs (version controlled there)
   # CONTEST_LOGS_REPORTS/Logs/ can remain for user data
   ```

### Phase 2: Update Scripts

**Web regression test script:**
```python
# Use test data directory
TEST_DATA_DIR = os.path.join('regression_baselines', 'Logs')

def get_test_log_path(year, contest, callsign):
    """Get path to test log file."""
    return os.path.join(TEST_DATA_DIR, year, contest.lower(), f"{callsign.lower()}.log")
```

### Phase 3: Documentation

**Update README in test repo:**
```markdown
# Regression Test Data

## Test Logs

Test logs are stored in `Logs/` directory, organized by year and contest.

## Adding New Test Logs

1. Add log file to appropriate directory: `Logs/YYYY/contest-name/callsign.log`
2. Commit to test repository: `git add Logs/ && git commit -m "Add test log for ..."`
3. Update test case definitions if needed

## Baseline Archives

Baseline ZIP archives are stored in `web_baseline_*/` directories, versioned by release tag.
```

---

## Migration Considerations

### Backward Compatibility

**Issue:** Existing scripts reference `CONTEST_LOGS_REPORTS/Logs/`

**Solutions:**
1. **Environment Variable (Recommended):**
   - Set `TEST_DATA_DIR` or `CONTEST_INPUT_DIR` to test repo location
   - Scripts use environment variable
   - Flexible, can point to different locations

2. **Path Updates:**
   - Update all script references
   - More explicit, less flexible

3. **Symlink (If Needed):**
   - Create symlink for backward compatibility
   - Platform-specific (Windows vs Linux)

**Recommendation:** Use environment variable approach

### Duplication in ZIP Archives

**Current:** Logs duplicated in ZIP archives

**Options:**
1. **Keep Duplication:**
   - ZIP archives are self-contained
   - Can extract and run tests from ZIP
   - Larger archives

2. **Remove from ZIPs:**
   - Smaller archives
   - Need logs separately to run tests
   - Less self-contained

**Recommendation:** Keep logs in ZIPs for self-contained archives, but don't rely on ZIPs as source of test logs

---

## CI/CD Considerations

**Test Data Access:**
- CI/CD needs access to test logs
- Test logs in local git repo (not pushed to GitHub)
- Options:
  1. **CI/CD clones test repo separately** (if moved to separate remote)
  2. **CI/CD uses test data from main repo** (if kept in main repo)
  3. **CI/CD uses test data from artifact storage** (if using cloud storage)

**For Local-Only Test Repo:**
- CI/CD would need test data from another source
- Could bundle test data in CI/CD setup
- Could use separate test data repository (if needed for CI/CD)

**Recommendation:** For now, local-only is fine. If CI/CD needs test data, can:
- Create separate test data repository (pushed to GitHub)
- Or bundle test data in CI/CD setup
- Or use artifact storage

---

## Recommendations Summary

### ✅ Recommended: Test Data in Test Repository

**Structure:**
```
regression_baselines/              # Local git repo
  .git/
  README.md
  Logs/                            # Version controlled test logs
    2024/
    2025/
  web_baseline_*/                  # Baseline ZIP archives
```

**Benefits:**
- ✅ Version controlled (reproducibility)
- ✅ Co-located with baselines (single test repository)
- ✅ Can track test data changes
- ✅ Clear separation from production data
- ✅ Reproducible across developers

**Implementation:**
- Use environment variable for paths (`TEST_DATA_DIR`)
- Update scripts to use test data directory
- Commit test logs to test repository
- Document test data management process

**Migration:**
- Copy existing logs to test repo
- Update script paths (use environment variable)
- Commit to test repository
- Update documentation

---

## Open Questions

1. **CI/CD Access:** How will CI/CD access test data if test repo is local-only?
   - Option: Separate test data repo (pushed to GitHub) for CI/CD
   - Option: Bundle test data in CI/CD setup
   - Option: Use artifact storage

2. **User Data vs Test Data:** Should `CONTEST_LOGS_REPORTS/Logs/` remain for user data?
   - Recommendation: Yes, keep for user uploads, separate from test data

3. **ZIP Archive Contents:** Keep logs in ZIPs or remove?
   - Recommendation: Keep for self-contained archives

---

**Last Updated:** 2026-01-20  
**Status:** Discussion/Decision

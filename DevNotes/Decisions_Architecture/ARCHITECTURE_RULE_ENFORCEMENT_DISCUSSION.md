# Architecture Rule Enforcement - Discussion and Recommendations

## Current State: Problem Identification

### The Problem

**Current Detection Method:**
- Architecture violations are detected **after the fact** in code summaries
- Relies on human review of AI-generated summaries
- Unreliable because:
  - Summaries may not highlight architectural violations
  - Violations may be subtle and easy to miss
  - Review burden falls on user, not automation
  - No immediate feedback to AI agent during code generation

### Example Violation

**What happened:**
- AI proposed using `ScoreStatsAggregator` directly instead of respecting contest-specific `time_series_calculator` plugins
- Violation of principle: "Contest-specific weirdness is implemented in code (plugins)"
- Only caught because user understood architecture and spotted it in analysis

**Why it wasn't caught:**
- No automated check for "does this respect plugin architecture?"
- No validation that aggregators use contest-specific plugins
- No rule in AI_AGENT_RULES.md about plugin architecture
- No pre-commit or code validation

## Solution Components

### 1. Enhanced AI Agent Rules Documentation

**Add to `Docs/AI_AGENT_RULES.md`:**

#### New Section: Contest-Specific Plugin Architecture

**CRITICAL: Contest-Specific Logic Must Use Plugins**

**Core Principle:** "Contest-specific weirdness is implemented in code (plugins/aggregators)"

**Rules:**

1. **DO NOT bypass contest-specific plugins or calculators.**
   - If a contest defines a `time_series_calculator` (e.g., `wae_calculator`, `naqp_calculator`), use it as the authoritative source
   - If a contest defines a `scoring_module` (e.g., `arrl_10_scoring`), respect it
   - Do NOT create alternative calculation paths that ignore plugins

2. **DO use plugins as single source of truth.**
   - Score calculators (`time_series_calculator`) are authoritative for final scores
   - Scoring modules (`scoring_module`) are authoritative for point calculation
   - Aggregators should use plugin output when available

3. **DO validate architectural compliance before proposing solutions.**
   - Before proposing changes, verify: Does this respect plugin architecture?
   - Before creating aggregators, verify: Should this use an existing plugin?
   - Before modifying scoring, verify: Does this respect contest-specific calculators?

4. **DO add validation warnings if multiple calculation paths exist.**
   - If aggregator calculates independently of plugin, add validation check
   - Warn if plugin and aggregator results differ
   - Use plugin as authoritative source, aggregator as validation

**Example Violations:**

```python
# WRONG: Bypassing contest-specific calculator
# ScoreStatsAggregator calculates score independently, ignoring time_series_calculator
final_score = total_points * total_mults  # Doesn't use log.time_series_score_df

# CORRECT: Using calculator as source of truth
if hasattr(log, 'time_series_score_df') and not log.time_series_score_df.empty:
    final_score = int(log.time_series_score_df['score'].iloc[-1])  # Uses plugin
else:
    final_score = calculate_fallback()  # Fallback only if plugin unavailable
```

**Architecture Decision Check:**

Before implementing changes that affect scoring/data calculation:
1. **Check contest definition:** Does contest have `time_series_calculator` or `scoring_module`?
2. **Check plugin availability:** Is plugin output available (`log.time_series_score_df`)?
3. **Respect plugin:** Use plugin as authoritative source
4. **Validate consistency:** Add validation if multiple paths exist

### 2. Automated Architecture Validation

**New File: `contest_tools/utils/architecture_validator.py`**

**Purpose:** Validate architectural compliance at runtime

**Features:**

```python
class ArchitectureValidator:
    """Validates architectural compliance rules."""
    
    def validate_scoring_consistency(self, log: ContestLog) -> List[str]:
        """
        Validates that scoring calculations are consistent with plugins.
        Returns list of warnings if inconsistencies found.
        """
        warnings = []
        
        # Check if calculator output exists
        if hasattr(log, 'time_series_score_df') and not log.time_series_score_df.empty:
            calc_final_score = int(log.time_series_score_df['score'].iloc[-1])
            
            # Calculate via ScoreStatsAggregator for comparison
            score_agg = ScoreStatsAggregator([log])
            agg_result = score_agg.get_score_breakdown()
            agg_final_score = agg_result["logs"].get(callsign, {}).get('final_score', 0)
            
            # Warn if they differ (within tolerance for rounding)
            if abs(calc_final_score - agg_final_score) > 1:
                warnings.append(
                    f"Scoring inconsistency detected: Calculator={calc_final_score}, "
                    f"Aggregator={agg_final_score}. Calculator should be authoritative."
                )
        
        return warnings
    
    def validate_dal_compliance(self, report_code: str) -> List[str]:
        """
        Validates that report code follows DAL pattern.
        Checks for anti-patterns like manual pivot tables, groupby, etc.
        """
        warnings = []
        # Static analysis or runtime checks for DAL violations
        return warnings
```

**Usage:**

- Call during report generation to warn about inconsistencies
- Log warnings to help detect violations early
- Optionally raise exceptions in strict mode

### 3. Pre-Commit Architecture Checks

**New File: `.git/hooks/pre-commit-architecture`**

**Purpose:** Validate architectural rules before commits

**Checks:**

1. **Plugin Usage Validation:**
   - Scan for changes to aggregators
   - Check if changes respect `time_series_calculator` plugins
   - Warn if aggregators bypass plugin architecture

2. **DAL Pattern Validation:**
   - Scan for manual data processing in reports
   - Check for pivot tables, groupby in report code
   - Warn if reports process data instead of using aggregators

3. **Scoring Consistency:**
   - Run `ArchitectureValidator.validate_scoring_consistency()` on sample logs
   - Fail if inconsistencies detected (optional)

**Implementation:**

```bash
#!/bin/bash
# .git/hooks/pre-commit-architecture

python -m contest_tools.utils.architecture_validator --pre-commit
```

### 4. AI Agent Self-Validation

**Enhancement to AI Agent Behavior:**

**Before proposing code changes, AI agent should:**

1. **Check Architecture Rules:**
   - Review relevant sections of `AI_AGENT_RULES.md`
   - Identify applicable architectural patterns
   - Verify proposal complies with rules

2. **Analyze Impact:**
   - Check if changes affect contest-specific plugins
   - Verify plugin architecture is respected
   - Identify potential violations

3. **Propose Validation:**
   - Suggest adding validation checks if multiple paths exist
   - Recommend using plugin as authoritative source
   - Flag potential architectural violations in analysis

**Example AI Agent Checklist:**

```
Before implementing scoring/data changes:
□ Does contest have time_series_calculator or scoring_module?
□ Is plugin output available (log.time_series_score_df)?
□ Does my solution use plugin as authoritative source?
□ Am I creating an alternative calculation path that bypasses plugins?
□ Should I add validation to detect inconsistencies?
```

### 5. Code Review Checklist Template

**Add to `Docs/AI_AGENT_RULES.md`:**

**Architecture Compliance Checklist:**

When reviewing code changes, verify:
- [ ] **Plugin Architecture:** Does code respect contest-specific plugins/calculators?
- [ ] **DAL Pattern:** Does code use aggregators instead of manual data processing?
- [ ] **Single Source of Truth:** Is there only one authoritative source for calculations?
- [ ] **Validation:** Are validation checks in place if multiple paths exist?
- [ ] **Documentation:** Are architectural decisions documented?

### 6. Automated Testing

**New Test File: `test_code/test_architecture_compliance.py`**

**Purpose:** Unit tests to validate architectural compliance

**Tests:**

```python
def test_scoring_plugin_consistency():
    """Test that calculator and aggregator scores match."""
    # Load sample log with calculator
    # Get score from calculator
    # Get score from aggregator
    # Assert they match (within tolerance)
    pass

def test_dal_pattern_compliance():
    """Test that reports don't process raw data."""
    # Scan report code for anti-patterns
    # Check for manual pivot tables, groupby, etc.
    # Assert violations not found
    pass

def test_plugin_respect():
    """Test that aggregators respect contest-specific plugins."""
    # Load contest with custom calculator
    # Verify aggregator uses calculator output
    # Assert no bypass of plugin
    pass
```

**Run in CI/CD:**
- Include in regression test suite
- Run on every PR
- Fail if violations detected

### 7. Documentation Structure

**Enhance `Docs/AI_AGENT_RULES.md`:**

**Add Architecture Decision Framework:**

```markdown
## Architecture Decision Framework

When making changes that affect data calculation or contest-specific logic:

### Step 1: Identify Architecture Requirements
- Does contest have plugin/calculator defined?
- What is the authoritative source for this calculation?
- Are there existing patterns to follow?

### Step 2: Verify Compliance
- Does my solution use the plugin/calculator?
- Am I creating alternative paths that bypass architecture?
- Are multiple calculation paths necessary (with validation)?

### Step 3: Validate Consistency
- If multiple paths exist, add validation checks
- Use plugin as authoritative source
- Warn if results differ significantly

### Step 4: Document Decision
- Document why this approach respects architecture
- Explain if fallback paths are needed
- Note any validation checks added
```

## Implementation Priority

### Phase 1: Immediate (Documentation)
1. ✅ Add plugin architecture rules to `AI_AGENT_RULES.md`
2. ✅ Add architecture decision framework
3. ✅ Add checklist to code review process

### Phase 2: Short-term (Validation)
1. Create `ArchitectureValidator` utility
2. Add validation calls to critical paths
3. Log warnings when violations detected

### Phase 3: Medium-term (Automation)
1. Add pre-commit hooks for architecture validation
2. Create architecture compliance tests
3. Add to CI/CD pipeline

### Phase 4: Long-term (AI Agent Enhancement)
1. Enhance AI agent self-validation
2. Add architecture rule checking to agent workflow
3. Automate architecture violation detection in summaries

## Benefits

### Immediate Benefits
- **Clear rules:** AI agents have explicit guidance on architecture
- **Early detection:** Validation catches violations before deployment
- **Consistency:** All code follows same architectural patterns

### Long-term Benefits
- **Reduced violations:** Automated checks prevent common mistakes
- **Faster reviews:** Checklists make human review more efficient
- **Better documentation:** Architecture decisions are explicit and searchable

## Trade-offs

### Pros
- Catches violations early (not relying on human review)
- Makes architectural rules explicit
- Provides automated validation

### Cons
- Additional complexity (validation code)
- May slow down development (pre-commit checks)
- Requires maintenance (keeping rules current)

## Recommendation

**Implement Phase 1 immediately:** Add plugin architecture rules to `AI_AGENT_RULES.md`

This provides:
- Immediate benefit: AI agents have explicit rules
- No code changes required
- Foundation for future automation

Then proceed with Phases 2-4 incrementally based on priority and need.

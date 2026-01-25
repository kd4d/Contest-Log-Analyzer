# Regression Testing Strategy for Web Version - Discussion

**Date:** 2026-01-20  
**Status:** Discussion/Planning  
**Category:** Testing Strategy

---

## Executive Summary

This document discusses strategies for automated regression testing in the web version of Contest Log Analytics. The web version uses Django test client to generate reports dynamically in session directories and compare them against baseline ZIP archives.

**Goal:** Automatically detect errors introduced by code updates by comparing generated reports against a known-good baseline.

---

## Current State Analysis

### CLI Regression Testing (Existing)

**Current Approach:**
- `run_regression_test.py` archives baseline reports, runs test cases from `regressiontest.bat`, and compares outputs
- Compares file-by-file: JSON, CSV, TXT, HTML, ADI files
- Handles dynamic content (UUIDs, timestamps) via sanitization
- Uses difflib for text-based comparisons, pandas for CSV comparisons

**Test Cases:**
- 17 test cases covering multiple contests (CQ WW, ARRL SS, CQ 160, CQ WPX, ARRL 10, ARRL DX, IARU HF, WAE, NAQP)
- Uses CLI: `python main_cli.py --report all <log_files> --debug-data`
- Generates reports to `CONTEST_REPORTS_DIR/reports/`

**Strengths:**
- ✅ Comprehensive file-by-file comparison
- ✅ Handles multiple file types intelligently
- ✅ Sanitizes dynamic content (UUIDs, timestamps)
- ✅ Well-established baseline management

**Limitations:**
- ❌ CLI-only (doesn't test web pipeline)
- ❌ Doesn't test web-specific features (dashboards, interactive components)
- ❌ Doesn't test HTTP endpoints, session management, or web UI

### Web Application Architecture

**Report Generation:**
- Reports generated in session-specific directories: `MEDIA_ROOT/sessions/{session_id}/reports/`
- Uses `ManifestManager` to track artifacts via `session_manifest.json`
- Reports include: HTML (Plotly charts), JSON (dashboard data), TXT (text reports), PNG (images), CSV (processed data), ADI (exports)

**Key Artifacts:**
- `session_manifest.json` - Catalog of all generated reports
- `dashboard_context.json` - Dashboard state/context
- JSON artifacts: `json_score_report_dashboard_{callsign}.json`
- HTML artifacts: Interactive charts, breakdown reports
- Text artifacts: Score reports, breakdown reports, multiplier summaries

**Web-Specific Features:**
- Interactive dashboards (scoreboard, multiplier, QSO activity)
- JSON-based data hydration for web components
- Session-based report storage
- Downloadable ZIP archives

---

## Regression Testing Strategy Options

### Option 1: Archive-Based Report Comparison (Recommended)

**Concept:** Download and archive reports from web interface, compare against baseline

**Approach:**
1. **Baseline Creation:**
   - Run test cases through web interface (automated via Selenium/Playwright or API calls)
   - Download ZIP archives for each test case
   - Extract and archive reports in baseline directory structure
   - Store baseline metadata (session IDs, timestamps, file hashes)

2. **Regression Test Execution:**
   - Run same test cases through web interface
   - Download ZIP archives for new runs
   - Extract reports to temporary directory
   - Compare against baseline using existing `run_regression_test.py` comparison logic

3. **Comparison Strategy:**
   - Reuse existing file comparison logic (JSON, CSV, TXT, HTML, ADI)
   - Sanitize dynamic content (UUIDs, timestamps, session IDs)
   - Compare file-by-file or use manifest-based comparison

**Implementation:**
```python
# Pseudo-code structure
class WebRegressionTester:
    def create_baseline(self, test_cases):
        """Run test cases, download reports, archive as baseline."""
        for test_case in test_cases:
            session_id = self.run_web_analysis(test_case)
            zip_path = self.download_all_reports(session_id)
            self.extract_and_archive(zip_path, baseline_dir)
    
    def run_regression(self, test_cases, baseline_dir):
        """Run test cases, compare against baseline."""
        for test_case in test_cases:
            session_id = self.run_web_analysis(test_case)
            zip_path = self.download_all_reports(session_id)
            temp_dir = self.extract_to_temp(zip_path)
            failures = self.compare_against_baseline(temp_dir, baseline_dir)
```

**Pros:**
- ✅ Reuses existing comparison logic
- ✅ Tests full web pipeline (end-to-end)
- ✅ Tests downloadable ZIP format (user-facing)
- ✅ Can test web-specific features (dashboards, interactive components)
- ✅ Baseline management similar to CLI approach

**Cons:**
- ⚠️ Requires web server running (Django dev server or Docker)
- ⚠️ More complex than CLI (HTTP requests, session management)
- ⚠️ Slower than CLI (HTTP overhead, file downloads)
- ⚠️ Requires browser automation or API client

**Automation Options:**
- **Option A: API Client (Recommended)**
  - Use Django test client or requests library
  - POST to `/analyze/` endpoint with test logs
  - Poll progress endpoint, download ZIP when complete
  - Faster, no browser overhead

- **Option B: Browser Automation**
  - Use Selenium/Playwright to simulate user interactions
  - Upload files, wait for processing, download ZIP
  - Tests full user workflow (more realistic)
  - Slower, more complex

---

### Option 2: Direct Session Directory Comparison

**Concept:** Access session directories directly (bypass HTTP), compare reports in-place

**Approach:**
1. **Baseline Creation:**
   - Run test cases through web pipeline (via test client or direct function calls)
   - Copy session directories to baseline archive
   - Store baseline metadata

2. **Regression Test Execution:**
   - Run test cases through web pipeline
   - Compare session directories directly against baseline
   - Use existing comparison logic

**Implementation:**
```python
# Pseudo-code structure
class WebRegressionTester:
    def create_baseline(self, test_cases):
        """Run test cases, archive session directories."""
        for test_case in test_cases:
            session_id = self.run_web_analysis(test_case)
            session_path = os.path.join(MEDIA_ROOT, 'sessions', session_id)
            self.archive_session(session_path, baseline_dir)
    
    def run_regression(self, test_cases, baseline_dir):
        """Run test cases, compare session directories."""
        for test_case in test_cases:
            session_id = self.run_web_analysis(test_case)
            session_path = os.path.join(MEDIA_ROOT, 'sessions', session_id)
            failures = self.compare_session(session_path, baseline_dir)
```

**Pros:**
- ✅ Faster (no HTTP overhead, no ZIP extraction)
- ✅ Direct access to all artifacts (including manifest)
- ✅ Can use existing comparison logic directly
- ✅ Tests actual web pipeline code paths

**Cons:**
- ⚠️ Doesn't test HTTP endpoints (download, view endpoints)
- ⚠️ Doesn't test ZIP generation logic
- ⚠️ Requires direct filesystem access to session directories
- ⚠️ May miss web-specific issues (URL generation, path handling)

---

### Option 3: Hybrid Approach (CLI + Web)

**Concept:** Run both CLI and web regression tests, compare results

**Approach:**
1. **CLI Regression:** Continue using existing `run_regression_test.py`
2. **Web Regression:** Add web-specific regression tests
3. **Cross-Validation:** Compare CLI vs Web outputs for same test cases

**Implementation:**
- Keep existing CLI regression tests
- Add web regression test suite
- Optionally compare CLI vs Web outputs (should match for same inputs)

**Pros:**
- ✅ Maintains existing CLI regression tests
- ✅ Adds web-specific coverage
- ✅ Cross-validation catches discrepancies
- ✅ Incremental implementation (add web tests gradually)

**Cons:**
- ⚠️ Duplicate test execution (CLI + Web)
- ⚠️ More maintenance overhead
- ⚠️ Need to keep both test suites in sync

---

### Option 4: JSON Artifact Comparison (Lightweight)

**Concept:** Focus on JSON artifacts (dashboard data) as primary regression targets

**Approach:**
1. **Baseline Creation:**
   - Extract JSON artifacts from baseline sessions
   - Store canonical JSON (sorted keys, sanitized)

2. **Regression Test Execution:**
   - Extract JSON artifacts from new sessions
   - Compare JSON structure and values
   - Ignore HTML/text reports (derived from JSON)

**Rationale:**
- JSON artifacts contain core data (scores, multipliers, time-series)
- HTML/text reports are derived from JSON
- If JSON is correct, reports should be correct
- Faster comparison (fewer files)

**Pros:**
- ✅ Fast (fewer files to compare)
- ✅ Focuses on core data (not presentation)
- ✅ JSON comparison is straightforward
- ✅ Catches data calculation errors

**Cons:**
- ⚠️ Doesn't catch report generation bugs (HTML formatting, text layout)
- ⚠️ Doesn't test visual components (Plotly charts, images)
- ⚠️ May miss presentation-layer regressions

---

## Recommended Strategy: Option 1 (Archive-Based) with API Client

### Rationale

1. **End-to-End Testing:** Tests full web pipeline including HTTP endpoints
2. **User-Facing:** Tests downloadable ZIP format (what users actually download)
3. **Reusable Logic:** Can leverage existing comparison code from `run_regression_test.py`
4. **Automation-Friendly:** API client approach is fast and reliable
5. **Comprehensive:** Tests both data (JSON) and presentation (HTML, text reports)

### Implementation Plan

#### Phase 1: Test Infrastructure

**Create:** `test_code/web_regression_test.py`

**Components:**
1. **Web Test Client:**
   - Django test client or requests library
   - Functions to upload logs, poll progress, download ZIP
   - Session management

2. **Baseline Management:**
   - Create baseline from known-good version
   - Store baseline ZIPs or extracted reports
   - Baseline metadata (test case IDs, file hashes)

3. **Comparison Engine:**
   - Reuse comparison logic from `run_regression_test.py`
   - Extract ZIPs, compare file-by-file
   - Sanitize dynamic content (session IDs, UUIDs, timestamps)

#### Phase 2: Test Case Definition

**Test Cases:** Mirror CLI regression tests but via web interface

**Structure:**
```python
WEB_REGRESSION_TEST_CASES = [
    {
        'id': 'cq_ww_cw_3logs',
        'contest': 'CQ-WW',
        'logs': ['2024/cq-ww-cw/k3lr.log', '2024/cq-ww-cw/w3lpl.log', '2024/cq-ww-cw/k1lz.log'],
        # Logs are relative paths from TEST_DATA_DIR (regression_baselines/Logs/)
        'expected_artifacts': ['json_score_report_dashboard_k3lr.json', ...]
    },
    {
        'id': 'arrl_dx_cw_2logs',
        'contest': 'ARRL-DX-CW',
        'logs': ['2025/ARRL-DX-CW/k5zd.log', '2025/ARRL-DX-CW/aa3b.log'],
        # Paths match structure in regression_baselines/Logs/
    },
    # ... more test cases
]
```

**Test Data Location:**
- Test logs stored in `regression_baselines/Logs/` (version controlled)
- Test case definitions use relative paths (e.g., `2024/cq-ww-cw/k3lr.log`)
- Scripts resolve paths via: `os.path.join(TEST_DATA_DIR, relative_path)`
- `TEST_DATA_DIR` environment variable (default: `regression_baselines/Logs`)

**Test Coverage:**
- Same contests as CLI regression tests
- Single-log and multi-log scenarios
- Different contest types (symmetric, asymmetric, custom calculators)

#### Phase 3: Automation Integration

**Execution:**
- **Recommended:** Use helper script: `regression_baselines\run_tests.bat --create-baseline v1.0.0-alpha.10`
- **Manual:** `C:\Users\mbdev\miniforge3\envs\cla\python.exe test_code\web_regression_test.py --create-baseline v1.0.0-alpha.10`
- **Run tests:** `regression_baselines\run_tests.bat --baseline v1.0.0-alpha.10`
- CI/CD integration: Run on PRs, releases (future)

**Output:**
- Pass/Fail per test case
- Detailed diff for failures
- Summary report

---

## Implementation Details

### Web App Automation Readiness Assessment

**Current State: ✅ READY for Script-Based Archive Generation**

**Available Endpoints:**
- ✅ `POST /analyze/` - Accepts file uploads, returns redirect to dashboard
- ✅ `GET /analyze/progress/<request_id>/` - Polls analysis progress (returns JSON with step 1-5)
- ✅ `POST /report/<session_id>/download_all/` - Initiates ZIP creation, returns request_id
- ✅ `GET /report/<session_id>/download_all/?request_id=<id>` - Downloads completed ZIP
- ✅ Session management is automatic (session_id in redirect URL)

**Progress Tracking:**
- Progress stored in JSON files: `MEDIA_ROOT/progress/<request_id>.json`
- Steps: 1=Uploading, 2=Parsing, 3=Aggregating, 4=Generating, 5=Ready
- Polling interval: 500ms (matches frontend)

**ZIP Download Flow:**
1. POST to `/report/<session_id>/download_all/` → Returns `{'request_id': '...', 'status': 'ready'}`
2. Poll `/analyze/progress/<request_id>/` → Returns step 1 (Zipping), step 2 (Downloading), step 3 (Done)
3. GET `/report/<session_id>/download_all/?request_id=<id>` → Downloads ZIP file

**Automation Approach: Django Test Client (Recommended)**

**Why Django Test Client:**
- ✅ No external HTTP server needed
- ✅ Fast (in-process, no network overhead)
- ✅ Reliable (no port conflicts, no server startup)
- ✅ Can access internal Django state if needed
- ✅ Same code paths as production

### Web Test Client Implementation

**Option A: Django Test Client (Recommended)**
```python
from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
import time
import re

class WebRegressionTester:
    def __init__(self):
        self.client = Client()
    
    def run_analysis(self, log_paths, custom_cty_path=None):
        """Upload logs, wait for processing, return session_id."""
        # 1. Prepare file uploads
        files = {}
        for i, log_path in enumerate(log_paths):
            with open(log_path, 'rb') as f:
                files[f'log_file_{i+1}'] = SimpleUploadedFile(
                    os.path.basename(log_path), f.read()
                )
        
        # 2. Upload and get request_id
        data = {'request_id': f'req_{uuid.uuid4().hex[:9]}'}
        if custom_cty_path:
            with open(custom_cty_path, 'rb') as f:
                files['custom_cty_file'] = SimpleUploadedFile(
                    os.path.basename(custom_cty_path), f.read()
                )
        
        response = self.client.post('/analyze/', files, data=data, follow=True)
        
        # 3. Extract session_id from redirect URL
        # Format: /report/<session_id>/dashboard/
        session_id = None
        if hasattr(response, 'redirect_chain') and response.redirect_chain:
            redirect_url = response.redirect_chain[-1][0]
            match = re.search(r'/report/([^/]+)/dashboard/', redirect_url)
            if match:
                session_id = match.group(1)
        
        if not session_id:
            raise ValueError("Failed to extract session_id from response")
        
        # 4. Poll progress until complete (step 5)
        request_id = data['request_id']
        max_wait = 300  # 5 minutes timeout
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            progress_response = self.client.get(f'/analyze/progress/{request_id}/')
            progress_data = progress_response.json()
            step = progress_data.get('step', 0)
            
            if step >= 5:  # Ready
                return session_id
            
            time.sleep(0.5)  # Match frontend polling interval
        
        raise TimeoutError(f"Analysis did not complete within {max_wait} seconds")
    
    def download_reports(self, session_id):
        """Download ZIP archive, return path to saved file."""
        # 1. Initiate ZIP creation
        response = self.client.post(f'/report/{session_id}/download_all/')
        data = response.json()
        request_id = data.get('request_id')
        
        if not request_id:
            raise ValueError("Failed to get request_id for ZIP download")
        
        # 2. Poll progress until ZIP is ready (step 3)
        max_wait = 60  # 1 minute timeout
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            progress_response = self.client.get(f'/analyze/progress/{request_id}/')
            progress_data = progress_response.json()
            step = progress_data.get('step', 0)
            
            if step >= 3:  # Done
                break
            
            time.sleep(0.5)
        
        # 3. Download ZIP file
        download_response = self.client.get(
            f'/report/{session_id}/download_all/?request_id={request_id}'
        )
        
        # 4. Save to temp file
        import tempfile
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        temp_zip.write(download_response.content)
        temp_zip.close()
        
        return temp_zip.name
```

**Option B: Requests Library (Alternative)**
```python
import requests

class WebRegressionTester:
    def __init__(self, base_url='http://localhost:8000'):
        self.base_url = base_url
        self.session = requests.Session()
    
    def run_analysis(self, log_paths):
        """Upload logs via HTTP POST."""
        files = {}
        for i, log_path in enumerate(log_paths):
            files[f'log_file_{i+1}'] = open(log_path, 'rb')
        
        response = self.session.post(f'{self.base_url}/analyze/', files=files)
        # Extract session_id, poll progress
        return session_id
```

### Baseline Management

**Storage Strategy: Local-Only Git Archive**

**Rationale for Local-Only Storage:**
- Baseline ZIP files are large (potentially 10-100MB+ per test case)
- Binary files (ZIP archives) don't benefit from Git's diff capabilities
- Not source code - baselines are generated artifacts
- GitHub repository bloat concerns (large binary files slow down clones)
- Privacy/security: May contain test data that shouldn't be public
- Cost: GitHub LFS has storage limits and costs

**Recommended Approach: Separate Local Git Repository**

**Directory Structure:**
```
<project_root>/
  regression_baselines/          # Main repo: .gitignored
    .git/                         # Separate local git repo (never pushed)
    web_baseline_v1.0.0-alpha.8/
      cq_ww_cw_3logs.zip          # ZIP archives (not extracted)
      arrl_dx_cw_2logs.zip
      ...
    web_baseline_v1.0.0-alpha.9/
      ...
    README.md                     # Baseline management instructions
    .gitignore                    # Ignore extracted files, temp files
```

**Alternative: Extracted Structure (If Needed)**
```
regression_baselines/
  .git/                           # Separate local git repo
  web_baseline_v1.0.0-alpha.8/
    cq_ww_cw_3logs/
      reports/
        json_score_report_dashboard_k3lr.json
        score_report_k3lr.txt
        ...
    arrl_dx_cw_2logs/
      reports/
        ...
```

**Baseline Creation Workflow:**
```python
def create_baseline(version_tag):
    """Run all test cases, archive as baseline in local git repo."""
    baseline_repo_path = 'regression_baselines'
    baseline_dir = f'{baseline_repo_path}/web_baseline_{version_tag}'
    
    # Ensure baseline repo exists
    if not os.path.exists(f'{baseline_repo_path}/.git'):
        init_baseline_repo(baseline_repo_path)
    
    # Create version directory
    os.makedirs(baseline_dir, exist_ok=True)
    
    # Generate and store ZIP archives (RAW, UNSANITIZED)
    tester = WebRegressionTester()
    test_data_dir = os.environ.get('TEST_DATA_DIR', 'regression_baselines/Logs')
    
    for test_case in WEB_REGRESSION_TEST_CASES:
        # Resolve log paths relative to test data directory
        log_paths = [os.path.join(test_data_dir, log_path) for log_path in test_case['logs']]
        session_id = tester.run_analysis(log_paths)
        zip_path = tester.download_reports(session_id)
        
        # Store ZIP file (not extracted, not sanitized)
        # Archives preserve raw data - sanitization happens during comparison
        baseline_zip = os.path.join(baseline_dir, f"{test_case['id']}.zip")
        shutil.copy(zip_path, baseline_zip)
        
        # Cleanup temp file
        os.remove(zip_path)
    
    # Commit to local git repo
    commit_baseline(baseline_repo_path, version_tag)
```

**Local Git Repository Management:**

**Initialization:**
```bash
cd regression_baselines
git init
git config user.name "Regression Test System"
git config user.email "regression@local"
echo "*.tmp" > .gitignore
echo "__extracted__/" >> .gitignore
git add .gitignore
git commit -m "Initialize baseline repository"
```

**Version Tagging:**
```bash
cd regression_baselines
git add web_baseline_v1.0.0-alpha.8/
git commit -m "Add baseline v1.0.0-alpha.8"
git tag v1.0.0-alpha.8
```

**Baseline Retrieval:**
```python
def get_baseline(version_tag):
    """Retrieve baseline ZIP files for comparison."""
    baseline_dir = f'regression_baselines/web_baseline_{version_tag}'
    
    # Checkout specific version in baseline repo
    subprocess.run(['git', 'checkout', f'v{version_tag}'], 
                  cwd='regression_baselines')
    
    # Return path to baseline directory
    return baseline_dir

def compare_zip_archives(new_zip_path, baseline_zip_path):
    """Compare two ZIP archives (sanitize during comparison)."""
    import tempfile
    import zipfile
    
    # Extract both ZIPs to temp directories
    with tempfile.TemporaryDirectory() as new_temp:
        with tempfile.TemporaryDirectory() as baseline_temp:
            # Extract new ZIP
            with zipfile.ZipFile(new_zip_path, 'r') as zipf:
                zipf.extractall(new_temp)
            
            # Extract baseline ZIP
            with zipfile.ZipFile(baseline_zip_path, 'r') as zipf:
                zipf.extractall(baseline_temp)
            
            # Compare files (sanitize during comparison)
            failures = []
            new_files = set()
            for root, dirs, files in os.walk(new_temp):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, new_temp)
                    new_files.add(rel_path)
            
            baseline_files = set()
            for root, dirs, files in os.walk(baseline_temp):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, baseline_temp)
                    baseline_files.add(rel_path)
            
            # Check for missing files
            missing_in_baseline = new_files - baseline_files
            missing_in_new = baseline_files - new_files
            
            if missing_in_baseline:
                failures.append(f"New files not in baseline: {missing_in_baseline}")
            if missing_in_new:
                failures.append(f"Baseline files missing in new: {missing_in_new}")
            
            # Compare common files (with sanitization)
            common_files = new_files & baseline_files
            for rel_path in sorted(common_files):
                new_file = os.path.join(new_temp, rel_path)
                baseline_file = os.path.join(baseline_temp, rel_path)
                
                # Read and sanitize both files
                with open(new_file, 'r', encoding='utf-8', errors='ignore') as f:
                    new_content = _sanitize_web_content(f.read(), rel_path)
                
                with open(baseline_file, 'r', encoding='utf-8', errors='ignore') as f:
                    baseline_content = _sanitize_web_content(f.read(), rel_path)
                
                # Compare sanitized content
                if new_content != baseline_content:
                    # Generate diff
                    diff = list(difflib.unified_diff(
                        baseline_content.splitlines(keepends=True),
                        new_content.splitlines(keepends=True),
                        fromfile=f'baseline/{rel_path}',
                        tofile=f'new/{rel_path}'
                    ))
                    failures.append(f"File: {rel_path}\n" + "".join(diff))
            
            return failures
```

**Benefits of Local Git Archive:**
- ✅ Version control for baselines (can rollback, compare versions)
- ✅ Local-only (never pushed to GitHub)
- ✅ Git history for baseline changes
- ✅ Tag-based versioning (matches release versions)
- ✅ Can extract ZIPs on-demand for comparison
- ✅ No GitHub storage costs or limits

**Main Repository Integration:**

**`.gitignore` Addition:**
```gitignore
# Regression test baselines (local git repo, never pushed)
regression_baselines/
!regression_baselines/README.md
```

**Why Keep README.md:**
- Documents baseline management process
- Instructions for creating/updating baselines
- Version history reference
- Small text file, safe to track

**Baseline Repository Structure:**
```
regression_baselines/
  .git/                           # Local git repo (never pushed)
  README.md                       # Tracked in main repo
  .gitignore                      # Ignore extracted files
  web_baseline_v1.0.0-alpha.8/
    cq_ww_cw_3logs.zip
    arrl_dx_cw_2logs.zip
    ...
  web_baseline_v1.0.0-alpha.9/
    ...
```

**Workflow Integration:**

**Creating New Baseline:**
```bash
# 1. Run regression tests
python test_code/web_regression_test.py --create-baseline v1.0.0-alpha.9

# 2. Baseline script:
#    - Generates ZIP files
#    - Stores in regression_baselines/web_baseline_v1.0.0-alpha.9/
#    - Commits to local git repo
#    - Tags as v1.0.0-alpha.9
```

**Running Regression Tests:**
```bash
# 1. Specify baseline version
python test_code/web_regression_test.py --baseline v1.0.0-alpha.8

# 2. Test script:
#    - Checks out baseline version in local repo
#    - Extracts ZIPs to temp directory
#    - Runs tests, compares against baseline
#    - Reports differences
```

**Alternative: ZIP-Only Storage (Simpler)**

If Git versioning isn't needed, simpler approach:

**Directory Structure:**
```
regression_baselines/              # .gitignored in main repo
  web_baseline_v1.0.0-alpha.8/
    cq_ww_cw_3logs.zip
    arrl_dx_cw_2logs.zip
    manifest.json                  # Metadata (version, date, test cases)
  web_baseline_v1.0.0-alpha.9/
    ...
```

**Pros:**
- ✅ Simpler (no separate git repo)
- ✅ Still local-only (gitignored)
- ✅ Easy to manage (just ZIP files)

**Cons:**
- ❌ No version history
- ❌ Can't rollback or compare baseline versions
- ❌ Manual version management

**Recommendation:** Use local Git repository for version control benefits while keeping it local-only.

### Comparison Logic

**Reuse Existing Code:**
- Import `sanitize_content()` and `parse_adif_for_comparison()` from `contest_tools.utils.regression_test_utils`
- Comparison logic implemented in `web_regression_test.py` using extracted utilities
- Adapt for ZIP-extracted directories
- Extend sanitization for web-specific content (see "Dynamic Content Handling" section)

**Key Functions Available:**
- `sanitize_content()` - UUID and timestamp sanitization (from `contest_tools.utils.regression_test_utils`)
- `parse_adif_for_comparison()` - ADIF file comparison (from `contest_tools.utils.regression_test_utils`)
- Comparison logic implemented in `web_regression_test.py` using pandas for CSV comparison

**Sanitization Extensions:**
- See "Dynamic Content Handling" section for extended `_sanitize_web_content()` function
- Extends existing `sanitize_content()` from `contest_tools.utils.regression_test_utils`
- Adds web-specific patterns (session IDs, request IDs, media URLs)

---

## Alternative: Lightweight JSON-Only Approach

### If Full Archive Comparison is Too Heavy

**Simplified Strategy:**
1. Extract only JSON artifacts from sessions
2. Compare JSON structure and values
3. Ignore HTML/text reports (assume they're derived correctly from JSON)

**Pros:**
- ✅ Much faster (fewer files)
- ✅ Focuses on core data correctness
- ✅ Catches calculation errors (scores, multipliers)
- ✅ Easier to implement

**Cons:**
- ⚠️ Doesn't catch report generation bugs
- ⚠️ Doesn't test presentation layer

**Use Case:** Quick smoke tests, CI/CD integration

---

## Integration with Existing Infrastructure

### Relationship to Previous CLI Regression Tests

**Migration Complete:**
- CLI regression tests have been deprecated and removed
- Web regression tests provide comprehensive coverage of the web pipeline
- Utility functions from CLI tests extracted to shared utilities

**Shared Components:**
- Test case definitions based on previous CLI test cases
- Comparison utilities (sanitization, ADIF parsing) in `contest_tools.utils.regression_test_utils`
- Baseline management structure similar to previous approach

### CI/CD Integration

**GitHub Actions / GitLab CI:**
```yaml
# Pseudo-YAML
test:
  - name: Start Web Server
    run: python web_app/manage.py runserver &
  
  - name: Run Web Regression Tests
    run: python test_code/web_regression_test.py
```

---

## Open Questions & Considerations

### 1. Baseline Management

**Question:** How to version baselines?

**Decision:** Local-Only Git Repository (Separate from Main Repo)

**Rationale:**
- Baseline ZIP files are large (10-100MB+ per test case)
- Binary files don't benefit from GitHub's diff capabilities
- Not source code - generated artifacts
- GitHub repository bloat concerns
- Privacy: Test data may be sensitive
- Cost: GitHub LFS has limits

**Implementation:**
- Separate local git repository in `regression_baselines/`
- Never pushed to GitHub (local-only)
- Versioned with git tags matching release versions
- Main repo: `.gitignore` excludes `regression_baselines/` (except README.md)

**Benefits:**
- ✅ Version control for baselines
- ✅ Can rollback or compare baseline versions
- ✅ Tag-based versioning
- ✅ Local-only (no GitHub storage)
- ✅ Git history for baseline changes

**See "Baseline Management" section for detailed implementation.**

### 2. Test Data Management

**Question:** Where to store test logs?

**Decision:** Test logs in test data repository (`regression_baselines/Logs/`)

**Rationale:**
- ✅ Version controlled (reproducibility)
- ✅ Co-located with baselines (single test repository)
- ✅ Can track test data changes
- ✅ Clear separation from production/user data
- ✅ Reproducible across developers

**Structure:**
```
regression_baselines/              # Local git repo
  Logs/                            # Version controlled test logs
    2024/
      cq-ww-cw/
        k3lr.log
        ...
    2025/
      ...
  web_baseline_*/                  # Baseline ZIP archives
```

**Path Management:**
- Use environment variable: `TEST_DATA_DIR=regression_baselines/Logs`
- Scripts reference logs via `TEST_DATA_DIR` environment variable
- Flexible, can point to different locations if needed

**See:** `DevNotes/REGRESSION_TEST_DATA_MANAGEMENT_STRATEGY.md` for detailed analysis

### 3. Web Server Requirements

**Question:** How to ensure web server is available for tests?

**Options:**
- Assume dev server running (manual)
- Auto-start Django dev server in test script
- Use Docker Compose for consistent environment
- Use Django test framework (in-memory, no HTTP)

**Recommendation:** Django test framework (fastest, most reliable)

### 4. Performance Considerations

**Question:** How long will web regression tests take?

**Estimate:**
- CLI regression: ~5-10 minutes (17 test cases)
- Web regression: ~10-20 minutes (HTTP overhead, ZIP downloads)
- Combined: ~15-30 minutes

**Mitigation:**
- Run in parallel (if possible)
- Use lightweight JSON-only approach for quick checks
- Full archive comparison for release candidates

### 5. Dynamic Content Handling

**Question:** What web-specific dynamic content needs sanitization?

**Existing Sanitization (from `run_regression_test.py`):**
- ✅ Plotly UUIDs in HTML (8-4-4-4-12 hex digits) → `__UUID__`
- ✅ Timestamps in manifests → `__TIMESTAMP__`
- Located in `_sanitize_content()` function (lines 176-187)

**Web-Specific Dynamic Content to Add:**
- Session IDs (UUIDs in paths, filenames, URLs)
- Request IDs (progress polling, form submissions)
- Timestamps in dashboard_context.json
- File paths (relative to session directory)
- Media URLs (MEDIA_URL prefix may vary)

**Solution:** Extend existing sanitization logic from `run_regression_test.py`

**Extended Sanitization Function:**
```python
def _sanitize_web_content(content: str, filename: str) -> str:
    """Sanitize web-specific dynamic content for regression testing."""
    # Existing sanitization (from regression_test_utils)
    content = sanitize_content(content, filename)
    
    # Web-specific: Session IDs in paths/URLs
    content = re.sub(r'sessions/[a-f0-9-]{36}/', 'sessions/__SESSION_ID__/', content)
    content = re.sub(r'session_id["\']:\s*["\'][a-f0-9-]{36}["\']', 
                     'session_id": "__SESSION_ID__"', content)
    
    # Web-specific: Request IDs
    content = re.sub(r'req_[a-z0-9]+', '__REQUEST_ID__', content)
    content = re.sub(r'request_id["\']:\s*["\']req_[a-z0-9]+["\']', 
                     'request_id": "__REQUEST_ID__"', content)
    
    # Web-specific: Media URLs (may vary by deployment)
    content = re.sub(r'/media/sessions/', '__MEDIA_URL__sessions/', content)
    
    # Web-specific: Timestamps in dashboard_context.json
    if 'dashboard_context.json' in filename:
        content = re.sub(r'"timestamp":\s*"[^"]+"', '"timestamp": "__TIMESTAMP__"', content)
        content = re.sub(r'"created_at":\s*"[^"]+"', '"created_at": "__TIMESTAMP__"', content)
    
    return content
```

---

## Web Error Testing Strategy

### HTTP Error Testing (404s, Navigation Errors)

**Critical Web-Specific Testing:** The web version has navigation paths and artifact discovery that can fail in ways the CLI doesn't.

**Error Scenarios to Test:**

1. **404 Errors - Missing Resources:**
   - Missing session directory → `Http404("Session not found")`
   - Missing manifest → `Http404("Analysis manifest not found")`
   - Missing report file → `Http404("Report not found")`
   - Missing archive → `Http404("Archive not found")`

2. **Navigation Errors - Broken Links:**
   - Dashboard links to missing artifacts
   - Report viewer links to non-existent files
   - Download links to missing ZIP archives
   - Sub-dashboard navigation (QSO, Multiplier) with missing data

3. **Artifact Discovery Failures:**
   - Manifest exists but artifacts missing
   - JSON artifacts missing (fallback to slow path)
   - HTML artifacts missing (broken dashboard links)
   - Context file corrupted or missing

**Test Implementation:**

**Option A: HTTP Status Code Testing**
```python
def test_dashboard_404_errors(self):
    """Test that 404 errors are properly raised for missing resources."""
    # Test 1: Invalid session ID
    response = self.client.get('/report/invalid-session-id/dashboard/')
    self.assertEqual(response.status_code, 404)
    
    # Test 2: Valid session but missing manifest
    session_id = self.create_test_session(remove_manifest=True)
    response = self.client.get(f'/report/{session_id}/dashboard/multipliers/')
    self.assertEqual(response.status_code, 404)
    
    # Test 3: Missing report file
    session_id = self.create_test_session()
    response = self.client.get(f'/report/{session_id}/reports/nonexistent.txt')
    self.assertEqual(response.status_code, 404)
```

**Option B: Link Validation Testing**
```python
def test_dashboard_link_validation(self):
    """Test that all dashboard links point to existing resources."""
    session_id = self.create_test_session()
    
    # Load dashboard
    response = self.client.get(f'/report/{session_id}/dashboard/')
    self.assertEqual(response.status_code, 200)
    
    # Extract all links from HTML
    links = self.extract_links_from_html(response.content)
    
    # Verify each link resolves
    for link in links:
        if link.startswith('/report/'):
            link_response = self.client.get(link)
            self.assertIn(link_response.status_code, [200, 302], 
                         f"Broken link: {link}")
```

**Option C: Artifact Discovery Testing**
```python
def test_artifact_discovery_robustness(self):
    """Test artifact discovery handles missing artifacts gracefully."""
    session_id = self.create_test_session()
    
    # Test with missing JSON artifact (should fallback to slow path)
    self.remove_artifact(session_id, 'json_score_report_dashboard_*.json')
    response = self.client.get(f'/report/{session_id}/dashboard/')
    self.assertEqual(response.status_code, 200)  # Should still work
    
    # Test with missing HTML artifact (should show error or placeholder)
    self.remove_artifact(session_id, 'interactive_animation*.html')
    response = self.client.get(f'/report/{session_id}/dashboard/qso/')
    self.assertEqual(response.status_code, 200)  # Dashboard loads, but link broken
```

### Navigation Flow Testing

**Test Complete User Workflows:**

1. **Happy Path:**
   - Upload logs → Process → View dashboard → Navigate to sub-dashboards → View reports → Download ZIP
   - All links should work, no 404s

2. **Error Recovery:**
   - Missing artifact → Dashboard still loads → Shows error message or placeholder
   - Corrupted manifest → Falls back to context file
   - Missing context → Redirects to home

3. **Edge Cases:**
   - Single log vs multi-log (different artifact patterns)
   - Different contest types (different dashboard structures)
   - Old session format (backward compatibility)

**Implementation:**
```python
def test_complete_navigation_flow(self):
    """Test complete user workflow from upload to download."""
    # 1. Upload and process
    session_id = self.upload_and_process_test_logs()
    
    # 2. Main dashboard
    response = self.client.get(f'/report/{session_id}/dashboard/')
    self.assertEqual(response.status_code, 200)
    
    # 3. Extract and follow links
    links = self.extract_dashboard_links(response)
    
    # 4. Test each navigation path
    for link_name, link_url in links.items():
        nav_response = self.client.get(link_url)
        self.assertIn(nav_response.status_code, [200, 302],
                     f"Navigation failed: {link_name} -> {link_url}")
    
    # 5. Download ZIP
    download_response = self.client.get(f'/report/{session_id}/download_all/')
    self.assertEqual(download_response.status_code, 200)
    self.assertEqual(download_response['Content-Type'], 'application/zip')
```

### Regression Test Integration

**Add Error Testing to Regression Suite:**

1. **Baseline Validation:**
   - Ensure baseline sessions have all expected artifacts
   - Verify no broken links in baseline

2. **Regression Detection:**
   - Compare link counts (new vs baseline)
   - Detect new 404 errors (should be zero)
   - Verify artifact discovery still works

3. **Error Message Comparison:**
   - If error handling changes, compare error messages
   - Ensure error messages are user-friendly

**Test Structure:**
```python
class WebRegressionTestSuite:
    def test_data_regression(self):
        """Compare report data (JSON artifacts) against baseline."""
        # Existing data comparison logic
        
    def test_navigation_regression(self):
        """Test that navigation still works (no new 404s)."""
        # New: Navigation testing
        
    def test_error_handling_regression(self):
        """Test that error handling hasn't regressed."""
        # New: Error scenario testing
```

---

## Recommendations

### Immediate Action Items

1. **Start with Lightweight Approach:**
   - Implement JSON artifact comparison first
   - Quick to implement, catches core data errors
   - Can expand to full archive comparison later

2. **Use Django Test Framework:**
   - Fastest, most reliable
   - No external dependencies (browser, HTTP server)
   - Can test web pipeline code directly
   - Built-in HTTP status code testing

3. **Reuse Existing Infrastructure:**
   - Leverage `sanitize_content()` and `parse_adif_for_comparison()` from `contest_tools.utils.regression_test_utils`
   - Comparison logic implemented in `web_regression_test.py`
   - Test case definitions based on previous CLI test cases
   - Similar baseline management structure

4. **Add Web-Specific Testing:**
   - HTTP error testing (404s, navigation errors)
   - Link validation testing
   - Artifact discovery robustness testing
   - Navigation flow testing

### Long-Term Strategy

1. **Full Archive Comparison:**
   - Implement after lightweight approach proves useful
   - Tests complete user workflow
   - Catches presentation-layer bugs

2. **CI/CD Integration:**
   - Run on every PR
   - Block merges if regressions detected
   - Update baseline on releases

3. **Cross-Validation:**
   - Compare CLI vs Web outputs
   - Should match for same inputs
   - Catches discrepancies between pipelines

---

## Next Steps

1. **Discussion:** Review this document, decide on approach
2. **Prototype:** Implement lightweight JSON comparison
3. **Add Error Testing:** Implement HTTP 404 and navigation error tests
4. **Validate:** Run against existing test cases
5. **Expand:** Add full archive comparison if needed
6. **Integrate:** Add to CI/CD pipeline

## Implementation Priority

### Phase 1: Core Data Testing (High Priority)
- JSON artifact comparison
- Reuse `_sanitize_content()` from `run_regression_test.py`
- Basic HTTP status code validation

### Phase 2: Error Testing (High Priority)
- 404 error detection
- Navigation link validation
- Artifact discovery robustness

### Phase 3: Full Archive Testing (Medium Priority)
- Complete ZIP download and comparison
- All file types (HTML, TXT, PNG, CSV, ADI)
- Extended sanitization for web content

### Phase 4: Integration (Low Priority)
- CI/CD integration
- Automated baseline updates
- Cross-validation (CLI vs Web)

---

**Related Documents:**
- `test_code/web_regression_test.py` - Web regression test infrastructure
- `contest_tools/utils/regression_test_utils.py` - Shared regression test utilities
- `DevNotes/Decisions_Architecture/STANDARD_CALCULATOR_APPLIES_TO_IMPLEMENTATION_PLAN.md` - Testing strategy example

---

**Last Updated:** 2026-01-20  
**Status:** Discussion/Planning

# ARRL 10 Meter Public Log Archive Implementation Plan

## Overview

Implement public log archive integration for ARRL contests, starting with ARRL 10 Meter. This mirrors the CQ WW archive functionality but uses a different URL structure and HTML format.

---

## Current State

### Existing CQ WW Implementation:
- **Module**: `contest_tools/utils/log_fetcher.py`
- **Functions**: `fetch_log_index()`, `download_logs()`
- **URL Pattern**: `https://cqww.com/publiclogs/{year}{mode}/` (e.g., `2015cw`, `2015ph`)
- **HTML**: Directory listing with `.log` file links

### ARRL Archive Structure (Discovered):
- **Selector Page**: `https://contests.arrl.org/publiclogs.php?cn=10m`
- **Year Listing**: `https://contests.arrl.org/publiclogs.php?eid=21&iid=1073`
  - `eid` = Event ID (contest type)
  - `iid` = Instance ID (year/edition)
- **HTML**: Table format with callsign links in cells (8 per row)

---

## Implementation Requirements

### 1. Contest Code Mapping

**Problem**: ARRL uses contest codes like `cn=10m`, while our system uses `ARRL-10`.

**Solution**: Create mapping dictionary:
```python
ARRL_CONTEST_CODES = {
    'ARRL-10': '10m',
    'ARRL-DX-CW': 'dx',  # Need to verify
    'ARRL-DX-SSB': 'dx',  # Need to verify
    # ... other ARRL contests as they're added
}
```

### 2. Event ID & Instance ID Discovery

**Problem**: Need to discover `eid` and `iid` values for each contest/year combination.

**Options:**
- **Option A**: Scrape selector page to find year links, extract `eid`/`iid` from href
- **Option B**: Construct directly if pattern is predictable (test first)

**Recommendation**: Start with Option A (scrape), fallback to Option B if pattern emerges.

### 3. HTML Parsing Strategy

**Structure**:
```html
<table>
  <tr>
    <td><a href="...">CALLSIGN1</a></td>
    <td><a href="...">CALLSIGN2</a></td>
    ...
  </tr>
  ...
</table>
```

**Approach**: 
- Find table element
- Extract all `<a>` links from `<td>` cells
- Parse callsigns from link text or href
- Similar to CQ WW but table-based instead of directory listing

### 4. Mode Handling

**ARRL 10 Meter**: Single contest, no mode selection
**Other ARRL Contests**: May have modes (DX, Sweepstakes)

**Implementation**:
- For now, ARRL 10 doesn't need mode parameter
- Design to handle mode later for other contests
- Similar pattern to CQ WW's mode handling

---

## Implementation Plan

### Phase 1: Core Functions in `log_fetcher.py`

#### 1.1 Add ARRL Base URL
```python
ARRL_BASE_URL = "https://contests.arrl.org/publiclogs.php"
```

#### 1.2 Contest Code Mapping
```python
ARRL_CONTEST_CODES = {
    'ARRL-10': '10m',
    # Add others as needed
}
```

#### 1.3 Function: `_get_arrl_eid_iid(year: str, contest_code: str) -> tuple[str, str]`
**Purpose**: Discover `eid` and `iid` for a given contest/year.

**Approach**:
1. Load selector page: `publiclogs.php?cn={contest_code}`
2. Parse HTML to find year link for the specified year
3. Extract `eid` and `iid` from the link href (e.g., `?eid=21&iid=1073`)
4. Return `(eid, iid)`

**Alternative**: If pattern is predictable, construct directly:
- Test: Does `eid` stay constant per contest? Does `iid` increment yearly?
- If yes, cache first lookup, then construct

#### 1.4 Function: `fetch_arrl_log_index(year: str, contest_code: str) -> List[str]`
**Purpose**: Fetch list of available callsigns for ARRL contest/year.

**Steps**:
1. Get `eid`/`iid` using `_get_arrl_eid_iid()`
2. Load log listing page: `publiclogs.php?eid={eid}&iid={iid}`
3. Parse HTML table to extract callsigns from link text
4. Return sorted list of callsigns

**HTML Parsing**:
```python
soup = BeautifulSoup(response.text, 'html.parser')
table = soup.find('table')  # Find the log listing table
callsigns = []
for row in table.find_all('tr'):
    for cell in row.find_all('td'):
        link = cell.find('a')
        if link:
            callsign = link.text.strip()
            callsigns.append(callsign)
return sorted(list(set(callsigns)))
```

**Note**: For `download_arrl_logs()`, we'll need to re-parse the table to get the `q` parameters, OR cache them. See below.

#### 1.5 Function: `fetch_arrl_log_mapping(year: str, contest_code: str) -> Dict[str, str]`
**Purpose**: Fetch mapping of callsign -> encoded `q` parameter for downloads.

**Steps**:
1. Get `eid`/`iid` using `_get_arrl_eid_iid()`
2. Load log listing page: `publiclogs.php?eid={eid}&iid={iid}`
3. Parse HTML table to extract both callsign and `q` parameter from each link
4. Return dictionary: `{callsign: q_parameter}`

**HTML Parsing**:
```python
soup = BeautifulSoup(response.text, 'html.parser')
table = soup.find('table')
mapping = {}
for row in table.find_all('tr'):
    for cell in row.find_all('td'):
        link = cell.find('a', href=True)
        if link:
            callsign = link.text.strip()
            href = link.get('href', '')
            # Extract q parameter from href: "showpubliclog.php?q=<encoded>"
            if 'showpubliclog.php?q=' in href:
                q_param = href.split('q=', 1)[1]
                mapping[callsign] = q_param
return mapping
```

**Rationale**: Need to store the `q` parameter mapping because we can't construct it - it's unique per callsign.

#### 1.6 Function: `download_arrl_logs(callsigns: List[str], year: str, contest_code: str, output_dir: str) -> List[str]`
**Purpose**: Download specific log files for ARRL contest.

**Steps**:
1. Get `eid`/`iid` using `_get_arrl_eid_iid()`
2. Fetch log mapping (callsign -> `q` parameter) using `fetch_arrl_log_mapping()`
3. For each callsign:
   - Get `q` parameter from mapping
   - Construct URL: `https://contests.arrl.org/showpubliclog.php?q={q_param}`
   - Download log file (returns Cabrillo text directly, not a redirect)
   - Save to `output_dir/{callsign}.log`
   - Return list of downloaded file paths

**Log File URL Pattern**: **CONFIRMED**
- **Pattern**: `https://contests.arrl.org/showpubliclog.php?q={encoded_parameter}`
- **Returns**: Direct Cabrillo log file content (200 OK, `text/plain;charset=UTF-8`)
- **Parameter**: `q` parameter is unique per callsign, obtained from log listing table
- **Note**: The `q` parameter appears to be encoded/encrypted, cannot be constructed - must be scraped from the table

**Implementation**:
```python
ARRL_BASE_URL = "https://contests.arrl.org"

mapping = fetch_arrl_log_mapping(year, contest_code)
downloaded_paths = []

for call in callsigns:
    q_param = mapping.get(call.upper())
    if not q_param:
        logger.warning(f"No q parameter found for {call}")
        continue
    
    file_url = f"{ARRL_BASE_URL}/showpubliclog.php?q={q_param}"
    local_path = os.path.join(output_dir, f"{call.lower()}.log")
    
    try:
        response = requests.get(file_url, timeout=15)
        response.raise_for_status()
        
        with open(local_path, 'wb') as f:
            f.write(response.content)
        
        downloaded_paths.append(local_path)
        logger.info(f"Downloaded: {call}.log")
    except Exception as e:
        logger.error(f"Failed to download {call}.log: {e}")

return downloaded_paths
```

---

### Phase 2: Web App Integration

#### 2.1 Update `views.py` - `get_log_index_view`

**Current** (CQ WW only):
```python
def get_log_index_view(request):
    contest = request.GET.get('contest')
    year = request.GET.get('year')
    mode = request.GET.get('mode')
    
    if contest == 'CQ-WW' and year and mode:
        callsigns = fetch_log_index(year, mode)
        return JsonResponse({'callsigns': callsigns})
```

**Updated**:
```python
def get_log_index_view(request):
    contest = request.GET.get('contest')
    year = request.GET.get('year')
    mode = request.GET.get('mode')
    
    if contest == 'CQ-WW' and year and mode:
        callsigns = fetch_log_index(year, mode)
        return JsonResponse({'callsigns': callsigns})
    elif contest == 'ARRL-10' and year:
        # ARRL 10 doesn't have modes
        from contest_tools.utils.log_fetcher import fetch_arrl_log_index
        contest_code = '10m'  # Map from contest name
        callsigns = fetch_arrl_log_index(year, contest_code)
        return JsonResponse({'callsigns': callsigns})
    # ... other ARRL contests later
```

#### 2.2 Update `views.py` - `analyze_logs` (fetch_callsigns branch)

**Current**:
```python
log_paths = download_logs(callsigns, year, mode, session_path)
```

**Updated**:
```python
if contest == 'CQ-WW':
    log_paths = download_logs(callsigns, year, mode, session_path)
elif contest == 'ARRL-10':
    from contest_tools.utils.log_fetcher import download_arrl_logs
    contest_code = '10m'
    log_paths = download_arrl_logs(callsigns, year, contest_code, session_path)
```

#### 2.3 Update `home.html` - Add ARRL-10 to contest dropdown

**Current**:
```html
<select class="form-select" id="archiveContest">
    <option value="" selected>Select Contest...</option>
    <option value="CQ-WW">CQ World Wide DX</option>
</select>
```

**Updated**:
```html
<select class="form-select" id="archiveContest">
    <option value="" selected>Select Contest...</option>
    <option value="CQ-WW">CQ World Wide DX</option>
    <option value="ARRL-10">ARRL 10 Meter</option>
</select>
```

#### 2.4 Update JavaScript in `home.html` - Contest selection logic

**Current**: Only enables year/mode for CQ-WW.

**Updated**:
```javascript
contestSelect.addEventListener('change', function() {
    if (this.value === 'CQ-WW') {
        yearSelect.disabled = false;
        // Mode enabled after year selection
    } else if (this.value === 'ARRL-10') {
        yearSelect.disabled = false;
        modeSelect.disabled = true;  // ARRL 10 has no modes
        slotsDiv.classList.add('d-none');
    } else {
        yearSelect.disabled = true;
        modeSelect.disabled = true;
        slotsDiv.classList.add('d-none');
    }
});
```

**Also update mode selection handler**:
```javascript
modeSelect.addEventListener('change', function() {
    const contest = contestSelect.value;
    if (this.value && (contest === 'CQ-WW' || contest === 'ARRL-10')) {
        // Fetch index for both CQ-WW and ARRL-10
        fetch(`/analyze/api/get_log_index/?contest=${contest}&year=${year}&mode=${mode || ''}`)
        // ...
    }
});
```

---

## Testing Plan

### Unit Tests:
1. **`_get_arrl_eid_iid()`**:
   - Test with known contest/year (ARRL-10, 2024)
   - Verify returns correct `eid`/`iid`
   - Test error handling (invalid year, contest not found)

2. **`fetch_arrl_log_index()`**:
   - Test with known contest/year
   - Verify returns list of callsigns
   - Test parsing of table HTML
   - Test error handling

3. **`download_arrl_logs()`**:
   - Test downloading single log
   - Test downloading multiple logs
   - Test error handling (log not found, network error)

### Integration Tests:
1. **Web UI Flow**:
   - Select ARRL-10 from dropdown
   - Select year (verify mode is disabled)
   - Search for callsign
   - Verify typeahead works
   - Submit and verify download/analysis works

2. **End-to-End**:
   - Download 2-3 ARRL 10 logs from 2024
   - Verify analysis pipeline completes
   - Verify reports are generated correctly

---

## Open Questions / TODOs

### 1. Log File URL Pattern ✅ **CONFIRMED**
**Pattern Discovered**: `https://contests.arrl.org/showpubliclog.php?q={encoded_parameter}`
- Each callsign has a unique `q` parameter in the log listing table
- The `q` parameter is encoded/encrypted, cannot be constructed - must be scraped
- `showpubliclog.php` returns the Cabrillo log file directly (200 OK, `text/plain`)
- **Implementation**: Must scrape table to get both callsign AND `q` parameter, store as mapping

### 2. Event ID / Instance ID Pattern
**Question**: Is `eid` constant per contest? Does `iid` increment yearly?
- **Investigation**: Test multiple years for ARRL-10 to see pattern
- If predictable, can cache first lookup, then construct
- If not, must scrape every time

### 3. Contest Code Mapping
**Need to verify**: 
- ARRL-DX-CW → `cn=dx?` (and mode selection?)
- ARRL-DX-SSB → `cn=dx?` (and mode selection?)
- Other ARRL contests → what codes?

### 4. Mode Handling for Other ARRL Contests
**ARRL 10**: No modes
**ARRL DX**: Likely has modes (CW/SSB) - how is this represented?
- Same contest code with mode parameter?
- Different `cn` codes?
- Mode selection in UI?

### 5. Error Handling
**Scenarios to handle**:
- Contest/year combination doesn't exist
- Network errors
- HTML structure changes (parsing fails)
- Missing callsigns
- Rate limiting (if any)

---

## Implementation Steps

### Step 1: Investigate Log File URL Pattern ✅ **COMPLETE**
- [x] Inspect actual `<a href>` from ARRL log listing page
- [x] Determine URL pattern for downloading logs: `showpubliclog.php?q={encoded_param}`
- [x] Document pattern in this plan

### Step 2: Implement Core Functions
- [ ] Add ARRL constants and mapping to `log_fetcher.py`
- [ ] Implement `_get_arrl_eid_iid()`
- [ ] Implement `fetch_arrl_log_index()` (returns callsigns only)
- [ ] Implement `fetch_arrl_log_mapping()` (returns callsign -> q parameter dict)
- [ ] Implement `download_arrl_logs()` (uses mapping to get q params)
- [ ] Add unit tests

### Step 3: Update Web App
- [ ] Update `get_log_index_view()` in `views.py`
- [ ] Update `analyze_logs()` fetch branch in `views.py`
- [ ] Update `home.html` contest dropdown
- [ ] Update JavaScript contest selection logic

### Step 4: Test
- [ ] Unit tests pass
- [ ] Manual UI testing
- [ ] End-to-end test with real logs

### Step 5: Documentation
- [ ] Update code comments
- [ ] Update user documentation (if needed)

---

## Risk Assessment

### High Risk:
- **HTML Structure Changes**: ARRL changes table format → breaks parsing
  - **Mitigation**: Robust error handling, clear error messages
  - **Same risk as CQ WW** (accepted)

### Medium Risk:
- **Event/Instance ID Changes**: ARRL changes ID system
  - **Mitigation**: Scraping approach is flexible
  - **Monitor**: Test periodically

### Low Risk:
- **URL Pattern Changes**: ARRL changes base URL structure
  - **Mitigation**: Constants in code, easy to update

---

## Future Extensions

### After ARRL-10 Works:
1. **Add ARRL DX** (CW/SSB modes)
2. **Add ARRL Sweepstakes** (CW/Phone modes)
3. **Add Other ARRL Contests** as definitions are added

### Refactoring Opportunities:
1. **Unify Archive Interface**: Create abstract base class for different archive types (CQ WW, ARRL, future archives)
2. **Configuration-Driven**: Move archive URLs/patterns to contest definitions JSON
3. **Caching**: Cache `eid`/`iid` lookups if pattern is predictable

---

## Notes

- **Fragility Warning**: This implementation relies on HTML scraping, same as CQ WW. Page structure changes will break functionality until fixed.
- **Mode Handling**: Start with ARRL-10 (no modes), design for future mode support.
- **Testing**: Prioritize testing with real ARRL 10 logs from 2024 before considering complete.

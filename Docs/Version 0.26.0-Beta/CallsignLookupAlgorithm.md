# Contest-Log-Analyzer/Docs/Version 0.26.0-Beta/CallsignLookupAlgorithm.md

# Callsign Lookup Algorithm Description

**Version: 0.26.2-Beta**

The algorithm determines a callsign's DXCC entity by processing it through a sequence of checks, ordered from most specific to most general. The first rule that provides a definitive answer stops the process.

### 1. Initial Cleanup

The raw callsign is first standardized. It's converted to uppercase, and common non-location suffixes like `/P` (portable), `/M` (mobile), or `-` are removed to isolate the core callsign for lookup.

### 2. Exact Callsign Match (Highest Priority)

The algorithm first checks if the cleaned callsign is an exact match for a special-case callsign defined in the country file (e.g., `=W1AW`). These entries override all other rules and are used for stations with unique operating locations or statuses. If an exact match is found, that entity is returned immediately.

### 3. Special Rule Checks

Next, a few hard-coded special rules are checked:

* **Maritime Mobile**: If the callsign ends in `/MM`, it is identified as a maritime station with no fixed country, and the process stops.

* **Guantanamo Bay (KG4)**: The algorithm specifically checks if the callsign fits the `KG4xx` (two-letter suffix) pattern. If it does, it's assigned to Guantanamo Bay. All other KG4 callsigns are correctly identified as standard United States stations later in the process.

### 4. Portable Operation Logic (/)

If the callsign contains a slash, it's treated as a portable operation. The logic uses a multi-step process to determine the location:

* **Unambiguous Prefix Match (High-Priority Rule)**: The algorithm first checks if either the part before the slash (A) or the part after (B) is an exact match for a prefix in the country file, but not both. If exactly one part is a valid prefix, that part is immediately identified as the location. This correctly resolves the vast majority of portable callsigns (e.g., `KH0/4Z5LA` -> Mariana Is., `EA8/W1AW` -> Canary Is.).

* **"Strip the Digit" Heuristic**: If the first check is inconclusive, the logic attempts to resolve prefixes that imply a numeric range (e.g., `CT` implies `CT1`, `CT2`, etc.). If a part of the call ends in a single digit (like `CT7`), that digit is stripped (`CT`), and the check for an unambiguous prefix match is run again.

* **Fallback for Ambiguous Calls**: If both checks are inconclusive, the algorithm proceeds to a structural analysis based on established conventions for US/Canadian callsigns versus others.

### 5. General Prefix Lookup (Longest Match)

If the callsign is not an exact match or a special case, the algorithm performs its primary function: a "longest prefix match." It starts with the full callsign and checks if it's a known prefix. If not, it shortens the callsign by one character from the right and checks again, repeating until it finds the longest valid prefix in its database (e.g., `VO2AC` -> `VO2A` -> `VO2`). The entity for that longest matching prefix is then returned.

### 6. WAE (Worked All Europe) Override

After the primary DXCC entity has been determined, a second lookup is performed specifically against the WAE (Worked All Europe) country list. If a WAE-specific entry is found for the callsign (e.g., `*4U1V` for Vienna Intl Ctr), the geographic data from that WAE entry (Continent, CQ Zone, ITU Zone) will override the data from the standard DXCC lookup. This is critical for contests like CQ WW, where entities like `*TA1` (European Turkey) must be correctly placed in Europe for scoring, even though the primary DXCC entity for Turkey is in Asia.

### 7. Fallback

If, after all of these checks, no entity can be determined, the callsign is assigned to an "Unknown" entity.
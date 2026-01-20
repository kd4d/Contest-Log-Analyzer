# Release Announcement: v1.0.0-alpha.10

**Release Date:** January 20, 2026  
**Tag:** `v1.0.0-alpha.10`

---

## 🎯 What's New in This Release

We're excited to announce **v1.0.0-alpha.10**, a significant update that fixes critical multiplier calculation bugs for **ARRL 10 Meter** and similar contests, adds **ARRL DX contest support**, and improves the dashboard UI for better readability.

---

## 🐛 Critical Bug Fixes - Multiplier Calculations

### For ARRL 10 Meter and Similar Contests

If you've been analyzing ARRL 10 Meter logs, you may have noticed some discrepancies in the multiplier counts. This release fixes several critical calculation bugs:

**Fixed Issues:**
- ✅ **Score Summary 'ALL' Line** - Now correctly sums multipliers from CW and PH modes instead of showing a union
  - **Before:** ARRL 10 showed 51 US States in 'ALL' (incorrect)
  - **After:** Now shows 102 US States (51 + 51, correct!)

- ✅ **Breakdown Report Totals** - Totals row now matches Score Summary totals
  - **Example:** CW: 174, PH: 154, Total: 328 (now consistent across all reports)

- ✅ **CUMM Column** - Cumulative multiplier column now matches Score Summary TOTAL
  - Previously showed 315 instead of 328 for ARRL 10
  - Now correctly calculates: 328 = 174 + 154

**Impact:** If you've analyzed ARRL 10 Meter logs in previous versions, you may want to re-analyze them to get the corrected multiplier counts. All reports (Score Summary, Breakdown, Multiplier Dashboard) should now be consistent.

---

## 🆕 New Contest Support

### ARRL DX Contest

**ARRL DX Contest** is now fully supported with proper handling of:
- ✅ **Asymmetric Contest Rules** - Different multiplier types for W/VE vs DX entries
- ✅ **Location-Based Filtering** - Multiplier rules automatically filtered by your entry class
- ✅ **DXCC Countries** - Proper counting for W/VE entries (count DX stations worked)
- ✅ **States/Provinces** - Correct handling for DX entries (count US States + Canadian Provinces from W/VE stations worked)
- ✅ **Public Log Fetching** - Can fetch and analyze logs from ARRL public logs

**How to Use:**
1. Upload your ARRL DX log (either W/VE or DX entry)
2. The system automatically detects your entry class and applies the correct multiplier rules
3. Get the full suite of analysis reports with accurate multiplier counting

---

## ✨ UI Improvements

### Better Readability in Dashboard Tables

**The Problem:** Multiplier names in dashboard tables were too long, making columns cramped and hard to read.

**The Solution:** Multiplier names are now abbreviated for better space utilization:
- **Provinces** → **Provs**
- **Mexican States** → **Mex**
- **ITU Regions** → **Regs**

**Where You'll See It:**
- Scoreboard tables on the main dashboard
- Multiplier tabs in the Multiplier Dashboard
- All table headers and tab labels

**Impact:** Tables are now easier to read, with more room for the data itself. Abbreviations are intuitive and shouldn't cause confusion.

---

## 🔧 Other Improvements

### Multiplier Dashboard

- **Smarter Tab Display** - The "All Multipliers" tab is now hidden when a contest has only one multiplier type (like ARRL DX for W/VE entries). Cleaner, less cluttered interface!

---

## 📊 What Should You Test?

### Priority 1: ARRL 10 Meter Multiplier Calculations

If you have ARRL 10 Meter logs, please:
1. **Re-analyze** your logs with this version
2. **Verify** that the Score Summary 'ALL' line matches the TOTAL line
   - Example: 102 US States should match across all rows
3. **Check** that Breakdown Report totals match Score Summary totals
4. **Confirm** CUMM column matches Score Summary TOTAL

### Priority 2: ARRL DX Contest Support

If you have ARRL DX logs (W/VE or DX entries):
1. Upload your log and verify the correct multiplier types are shown
2. Check that multipliers are counted correctly for your entry class
3. Verify all reports generate without errors
4. Test public log fetching if applicable

### Priority 3: UI Improvements

1. Check that multiplier names in tables are readable and abbreviated
2. Verify tabs in Multiplier Dashboard look better with abbreviated labels
3. Confirm tables aren't cramped anymore

---

## 📝 Known Issues

**None in this release!** 🎉

---

## 🚀 How to Get This Update

### If Running via Docker:

```bash
cd /path/to/Contest-Log-Analyzer
git fetch origin --tags
git checkout v1.0.0-alpha.10
docker-compose down
docker-compose up --build -d
```

### If Running from Source:

```bash
cd /path/to/Contest-Log-Analyzer
git fetch origin --tags
git checkout v1.0.0-alpha.10
# Restart your web server as usual
```

---

## 🎁 What's Next?

We're continuing to improve multiplier calculations and add more contest support. Future releases will include:
- Additional contest definitions
- More UI polish and improvements
- Performance optimizations
- Additional analysis features

---

## 💬 Feedback and Issues

As always, we appreciate your testing and feedback! If you encounter any issues or have suggestions:

- Report bugs through your usual testing channel
- Share your experience with the new features
- Let us know if the multiplier fixes work correctly for your logs

**Thank you for being part of our beta testing program!** Your feedback helps make CLA better for everyone.

---

## 📚 Full Details

For complete technical details and a full list of changes, see:  
[Full Release Notes](RELEASE_NOTES_1.0.0-alpha.10.md)

---

**Happy Contesting!**  
KD4D - Contest Log Analytics Team

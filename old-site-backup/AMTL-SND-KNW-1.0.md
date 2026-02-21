# Socrates & Donuts — Known Issues Register
## Document Code: AMTL-SND-KNW-1.0
## Almost Magic Tech Lab
## 19 February 2026

> *This document follows AMTL-ECO-STD v1.0. All conventions defined there apply unless explicitly overridden with a Decision Register entry.*

---

## Status Codes

| Code | Meaning |
|------|---------|
| 🔴 | Open — known issue, no workaround |
| 🟡 | Workaround Available — issue exists but can be mitigated |
| 🟢 | Fixed — resolved in a specific version |
| ⚪ | Deferred — acknowledged but not prioritised |

---

## Known Issues

### KNW-001: localStorage Fragility (Website Mode)

| Field | Value |
|-------|-------|
| Status | 🟡 Workaround Available |
| Severity | Medium |
| Description | Website mode stores all user data in browser localStorage, which can be cleared by the user, browser cleanup tools, or incognito mode without warning |
| Root Cause | localStorage is the only zero-registration, zero-server storage option for a static website. It's inherently volatile |
| Workaround | Use the Export feature regularly to save a JSON backup. Import restores everything. Desktop mode uses SQLite and doesn't have this issue |
| Fix Required | Consider FileSystem Access API (OPFS) when browser support stabilises. Currently inconsistent across browsers |
| Date Logged | 19 February 2026 |

### KNW-002: Browser Timer Throttling During Forced Silence

| Field | Value |
|-------|-------|
| Status | 🟡 Workaround Available |
| Severity | Low |
| Description | When the browser tab is backgrounded, JavaScript timers are throttled, causing the Forced Silence timer to take longer than configured |
| Root Cause | Browser power-saving behaviour — tabs not in focus get reduced timer precision |
| Workaround | Keep S&D in the foreground during Forced Silence. Desktop mode (Electron) is not affected by this |
| Fix Required | Use Web Workers for timing (not affected by tab throttling) or use `requestAnimationFrame` with timestamp comparison |
| Date Logged | 19 February 2026 |

### KNW-003: Red Flag Detection False Positives

| Field | Value |
|-------|-------|
| Status | 🟡 Workaround Available |
| Severity | Low |
| Description | Phrase-based red flag detection may trigger on academic discussion of distress topics, or when the user is describing someone else's situation rather than their own |
| Root Cause | Rule-based phrase matching lacks context awareness — it can't distinguish between "I feel hopeless" (personal) and "the character felt hopeless" (discussion) |
| Workaround | Dismiss the grounding message and continue normally. S&D does not block the user — it pauses and checks in. False positives are preferable to false negatives for safety |
| Fix Required | If AI is connected, use sentiment analysis to add context before triggering. For rule-based mode, maintain a curated phrase list with regular review |
| Date Logged | 19 February 2026 |

### KNW-004: No Cross-Device Sync

| Field | Value |
|-------|-------|
| Status | ⚪ Deferred |
| Severity | Low |
| Description | There is no automatic sync between website mode and desktop mode, or between different browsers/devices |
| Root Cause | By design — S&D has no server-side component, so there is no sync infrastructure. This is a feature (privacy), not a bug |
| Workaround | Use Export/Import to move data between devices manually |
| Fix Required | Could add optional encrypted cloud sync in a future version, but this would compromise the "no server" principle. Deferred unless user demand is clear |
| Date Logged | 19 February 2026 |

### KNW-005: Question Bank English Only

| Field | Value |
|-------|-------|
| Status | ⚪ Deferred |
| Severity | Low |
| Description | The curated question bank is only available in English. No multi-language support |
| Root Cause | Each question is carefully crafted for philosophical precision — machine translation would lose nuance |
| Workaround | None for non-English speakers |
| Fix Required | Manual translation by native speakers for each target language. Parked for future consideration |
| Date Logged | 19 February 2026 |

### KNW-006: Contradiction Finder Limited Without AI

| Field | Value |
|-------|-------|
| Status | 🟡 Workaround Available |
| Severity | Medium |
| Description | In rule-based mode (no AI), the Contradiction Finder uses simple sentiment comparison which misses nuanced contradictions |
| Root Cause | Rule-based pattern matching cannot understand semantic meaning — it compares keywords and sentiment polarity, not conceptual consistency |
| Workaround | Connect an LLM for deeper contradiction analysis. The rule-based version still catches obvious contradictions ("I love my job" vs "I hate going to work") |
| Fix Required | Phase 2 enhancement — AI-powered contradiction detection when LLM is connected |
| Date Logged | 19 February 2026 |

---

## Summary

| Status | Count |
|--------|-------|
| 🔴 Open | 0 |
| 🟡 Workaround Available | 4 |
| 🟢 Fixed | 0 |
| ⚪ Deferred | 2 |
| **Total** | **6** |

---

## New Issue Template

```markdown
### KNW-XXX: [Title]

| Field | Value |
|-------|-------|
| Status | [🔴/🟡/🟢/⚪] |
| Severity | [Critical/High/Medium/Low] |
| Description | [What's happening] |
| Root Cause | [Why it's happening] |
| Workaround | [How to work around it, or "None"] |
| Fix Required | [What needs to be done to fix it] |
| Date Logged | [DD Month YYYY] |
```

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 19 February 2026 | Claude (Thalaiva) | Initial register — 6 known issues from design phase |

---

*Almost Magic Tech Lab*
*"Honest about what's not done. Clear about workarounds."*

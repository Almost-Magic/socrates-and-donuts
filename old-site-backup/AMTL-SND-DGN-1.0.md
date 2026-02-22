# Socrates & Donuts — Diagnostic Playbook
## Document Code: AMTL-SND-DGN-1.0
## Almost Magic Tech Lab
## 19 February 2026

> *This document follows AMTL-ECO-STD v1.0. All conventions defined there apply unless explicitly overridden with a Decision Register entry.*

---

## How to Use This Document

Find your symptom below. Follow the diagnosis steps. Apply the fix. If the fix doesn't work, escalate to the next level.

---

## Symptom 1: S&D Won't Start (Desktop Mode)

### Likely Causes
- Flask backend failed to start
- Port 5010 already in use
- Python environment broken
- Electron can't find Flask

### Diagnosis Steps

1. **Check if port 5010 is in use:**
   - Workshop status dashboard should show S&D's health
   - If green but app not visible → Electron issue, not Flask
   - If red → Flask didn't start

2. **Check Flask process:**
   - Workshop → S&D → View Logs
   - Look for startup errors in `logs/snd.log`

3. **Check port conflict:**
   - Workshop → Port Monitor → Is 5010 occupied by another process?

### Fix

| Cause | Fix |
|-------|-----|
| Port conflict | Workshop → Stop whatever is on 5010, then restart S&D |
| Flask crash | Workshop → Restart S&D (3-tier: simple → deep → full) |
| Python broken | Cline: reinstall requirements.txt |
| Electron issue | Workshop → Stop S&D fully, then relaunch |

### Escalation
If restart doesn't work → ELAINE diagnosis (Level 4) → reads MRD tree `snd-startup-failure`

---

## Symptom 2: No Daily Question Appearing

### Likely Causes
- Notification permission not granted
- Service worker not registered
- SMS not configured or TextBee down
- Question bank empty or corrupted

### Diagnosis Steps

1. **Check notification settings:**
   - Settings → Notifications → Is push enabled? Is the time set?
   
2. **Check browser permissions:**
   - Browser settings → Notifications → Is S&D allowed?

3. **Check question bank:**
   - `GET /api/question/today` → Does it return a question?
   - If empty → question bank issue

4. **Check SMS (if configured):**
   - Settings → SMS → Is TextBee API key valid?
   - Check TextBee dashboard for delivery status

### Fix

| Cause | Fix |
|-------|-----|
| Permission denied | Re-enable notifications in browser settings |
| Service worker gone | Hard refresh the website (Ctrl+Shift+R) |
| TextBee down | Disable SMS temporarily, rely on push |
| Question bank empty | Cline: verify `questions.json` exists and is valid |

---

## Symptom 3: AI Features Not Working

### Likely Causes
- No LLM connected
- API key invalid or expired
- Ollama not running (if using Ollama)
- Supervisor down (if using Supervisor-routed Ollama)
- Provider rate limit hit

### Diagnosis Steps

1. **Check connection:**
   - Settings → Connect AI → Click "Test Connection"
   - If it fails, the error message tells you why

2. **Check provider:**
   - Ollama: Is Ollama running? (`/api/health` on Supervisor :9000)
   - Cloud providers: Is the API key still valid? Check provider's dashboard

3. **Check health endpoint:**
   - `GET /api/health` → `llm_connected` field shows true/false

### Fix

| Cause | Fix |
|-------|-----|
| No LLM configured | Settings → Connect AI → set up a provider |
| Invalid API key | Replace the key in Settings → Connect AI |
| Ollama down | Workshop → Restart Supervisor, then Ollama |
| Rate limited | Wait, or switch to a different provider |
| Provider down | S&D continues without AI — all core features work |

---

## Symptom 4: Data Lost (Desktop)

### Likely Causes
- SQLite database file deleted or corrupted
- Application data directory moved or permissions changed
- Database locked by another process

### Diagnosis Steps

1. **Check database file:**
   - Does `~/.socrates-and-donuts/vault.db` exist?
   - Is it readable? (Check file size — 0 bytes means corrupted)

2. **Check permissions:**
   - Is the file read/write for the current user?

3. **Check for lock:**
   - Is `vault.db-wal` or `vault.db-shm` present? (WAL mode lock files)

### Fix

| Cause | Fix |
|-------|-----|
| File missing | Import from last JSON export (Settings → Import) |
| File corrupted | Delete vault.db, restart S&D (creates fresh), then import from JSON export |
| Permissions wrong | Fix file permissions to user read/write |
| Locked | Stop S&D, delete .wal and .shm files, restart |

**Prevention:** Export your vault regularly (Settings → Export). Keep the JSON file safe.

---

## Symptom 5: Data Lost (Website)

### Likely Causes
- Browser localStorage cleared (manually or by browser cleanup)
- Different browser or incognito mode
- Browser storage quota exceeded

### Diagnosis Steps

1. **Check localStorage:**
   - Browser DevTools → Application → Local Storage → Is `snd_sessions` present?

2. **Check browser:**
   - Are you using the same browser as before?
   - Is this an incognito/private window?

### Fix

| Cause | Fix |
|-------|-----|
| localStorage cleared | Import from last JSON export |
| Different browser | Open in the browser you used before, or export/import |
| Incognito mode | Incognito doesn't persist. Use a normal window |
| Quota exceeded | Export, clear old sessions, import what you need |

**Prevention:** Use the desktop app for long-term data. Use Export regularly if using the website.

---

## Symptom 6: Forced Silence Not Working

### Likely Causes
- JavaScript disabled
- Timer not starting (CSS animation issue)
- Browser tab backgrounded (timers throttled)

### Diagnosis Steps

1. **Check JavaScript:**
   - Is JS enabled in browser settings?
   
2. **Check tab focus:**
   - Browsers throttle timers in background tabs
   - Keep S&D in the foreground during silence

3. **Check for errors:**
   - Browser DevTools → Console → any red errors?

### Fix

| Cause | Fix |
|-------|-----|
| JS disabled | Enable JavaScript |
| Background throttling | Keep S&D in the foreground, or use the desktop app |
| JS error | Hard refresh (Ctrl+Shift+R) |

---

## Symptom 7: Safety Mode Triggered Incorrectly (False Positive)

### Likely Causes
- Red flag phrase detection matched normal text
- User was discussing a topic academically, not personally

### Diagnosis Steps

1. **Check what triggered it:**
   - The grounding message should appear
   - Review what you wrote — did it contain phrases that could indicate distress?

### Fix

This is intentionally cautious — false positives are better than false negatives when it comes to safety.

If you're fine and want to continue:
- Dismiss the grounding message
- Continue your session normally
- S&D will resume normal questioning

If you'd like to report a false positive:
- Note the phrase that triggered it
- Submit via GitHub Issues on `Almost-Magic/socrates-and-donuts`

---

## Escalation Levels

| Level | Action | Who/What | Time |
|-------|--------|----------|------|
| 0 | Self-heal | S&D's own health check + auto-restart | 0 seconds |
| 1 | Workshop simple restart | Stop and start Flask + Electron | 10 seconds |
| 2 | Workshop deep restart | Kill port, clear locks, restart | 30 seconds |
| 3 | Workshop full recovery | Full clean reinstall of dependencies + restart | 60 seconds |
| 4 | ELAINE diagnosis | Reads MRD trees, applies automated fix | 1–5 minutes |
| 5 | Cline/Guruve | Reads MRD, applies code fix, runs tests | 5–30 minutes |
| 6 | Mani notified | Reviews proposed fix, approves or redirects | Human decides |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 19 February 2026 | Claude (Thalaiva) | Initial playbook — 7 symptom categories with diagnosis and fix paths |

---

*Almost Magic Tech Lab*
*"Something broke — here's how to fix it."*

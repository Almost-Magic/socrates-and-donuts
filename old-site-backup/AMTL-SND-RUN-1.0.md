# Socrates & Donuts — Operations Runbook
## Document Code: AMTL-SND-RUN-1.0
## Almost Magic Tech Lab
## 19 February 2026

> *This document follows AMTL-ECO-STD v1.0. All conventions defined there apply unless explicitly overridden with a Decision Register entry.*

---

## 1. Service Summary

| Field | Value |
|-------|-------|
| App | Socrates & Donuts |
| Port | 5010 (Flask backend) |
| Health URL | `http://localhost:5010/api/health` |
| Data Location (Desktop) | `~/.socrates-and-donuts/vault.db` |
| Data Location (Website) | Browser localStorage |
| Log File | `logs/snd.log` |
| Process | `python -m app` (backend), Electron (frontend) |

---

## 2. Daily Operations

### Starting S&D (Desktop Mode)

**Via Workshop (preferred):**
Click "Socrates & Donuts" in The Workshop dashboard → Electron launches, Flask starts automatically.

**Via ELAINE:**
"Open Socrates and Donuts" → ELAINE triggers Workshop launch.

**Manual fallback (only if Workshop is down):**
Workshop handles this. If Workshop is also down, see AMTL-SND-DGN-1.0.

### Website Mode

No startup needed — it's a static site on GitHub Pages. Just open the URL in any browser.

### Daily Routine

1. S&D sends daily question at configured time (push notification and/or SMS)
2. User opens S&D — today's question is displayed
3. User reflects, responds (with or without Forced Silence)
4. Session saved automatically
5. "Did that land?" feedback collected
6. Insight optionally saved to vault

### Stopping S&D (Desktop Mode)

- Close the Electron window → S&D minimises to system tray (still running)
- Right-click tray icon → "Quit" → Flask backend stops, Electron exits
- Workshop "Stop" button → clean shutdown of both Flask and Electron

---

## 3. Interpreting the Health Endpoint

`GET http://localhost:5010/api/health`

| Field | Healthy | Warning | Critical |
|-------|---------|---------|----------|
| `status` | "healthy" | "degraded" | "unhealthy" |
| `vault_entries` | Any number | — | — |
| `llm_connected` | true (if configured) | false (if configured but failing) | — |
| `questions_in_bank` | 50+ | <50 | 0 |

---

## 4. Logs

| Log | Location | Contents |
|-----|----------|----------|
| Application log | `logs/snd.log` | Startup, errors, API calls, safety triggers |
| Session log | SQLite database | All session data (questions, responses, feedback) |

**Log rotation:** Logs rotate daily, 7 days retained. Configured in Flask logging setup.

**Reading logs:**
- Via ELAINE: "Show me Socrates and Donuts logs"
- Via Workshop: Log viewer panel for S&D
- Never via terminal (AMTL-ECO-STD Rule: No terminal for Mani)

---

## 5. Backup & Recovery

### What to Back Up

| Item | Location | Frequency |
|------|----------|-----------|
| Vault database | `~/.socrates-and-donuts/vault.db` | Weekly (or use export) |
| Settings | `~/.socrates-and-donuts/settings.json` | With vault backup |
| Question bank customisations | `app/data/questions_custom.json` | With code (in Git) |

### How to Back Up

**Recommended:** Use the Export feature in S&D Settings → Downloads complete vault as JSON file. Store the JSON file wherever you keep important files.

**Alternative:** The SQLite database file can be copied directly.

### Recovery

1. Install S&D fresh (desktop) or open website
2. Go to Settings → Import
3. Upload the JSON export file
4. All sessions, insights, letters, and settings restored

---

## 6. Updates & Maintenance

### Updating Desktop Version

1. Workshop checks for updates (if configured)
2. `git pull` in the S&D repository
3. `pip install -r requirements.txt --break-system-packages` (if dependencies changed)
4. Restart S&D via Workshop

### Updating Website Version

1. Push changes to `main` branch → GitHub Pages auto-deploys
2. Users get the update on next page load (service worker updates in background)

### Question Bank Updates

New questions are added to `app/data/questions.json` and committed to Git. Desktop users get them on next update. Website users get them on next deploy.

---

## 7. LLM Connection Management

### Checking LLM Status

The health endpoint shows `llm_connected: true/false` and `llm_provider`.

### Changing LLM Provider

1. Open S&D → Settings → Connect AI
2. Select provider from dropdown
3. Enter API key (stored locally only)
4. Click "Test Connection"
5. If successful, AI features become available

### If LLM Stops Working

- S&D continues to function — all non-AI features remain available
- Check if Ollama is running (if using Ollama)
- Check if API key is still valid (if using cloud provider)
- S&D never breaks because AI is down — it gracefully disables AI features

---

## 8. Notification Management

### Browser Push Notifications

- Configured in Settings → Notifications
- Requires browser permission (requested once, gently)
- Time configurable (default 7:00am)
- Can be disabled without losing any functionality

### SMS Notifications (Optional)

- Requires TextBee configuration
- Phone number stored locally
- Can be disabled in Settings

### If Notifications Stop

1. Check browser notification permissions
2. Check if S&D service worker is registered
3. For SMS: check TextBee API key and phone number in Settings

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 19 February 2026 | Claude (Thalaiva) | Initial runbook — daily ops, backup, LLM management |

---

*Almost Magic Tech Lab*
*"Day-to-day operations. Not building, not fixing — just running."*

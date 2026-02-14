# Almost Magic Tech Lab — App Registry

**Last Updated**: 2026-02-15
**Author**: Mani Padisetti

## Purpose

Single source of truth for all Almost Magic Tech Lab applications, their locations in the Dropbox folder, ports, and start commands.

## Active Applications

| # | App Name | Folder | GitHub Repo | Port | Stack | Start Command | Commit |
|---|----------|--------|-------------|------|-------|---------------|--------|
| 1 | Elaine | `Elaine-git` | `Elaine` | 5000 | Python/Flask | `python app.py` | `a5bf9a8` |
| 2 | Ripple CRM | `Ripple CRM` | `ripple` | 5001 | Node.js/Express/SQLite | `node server.js` | `44ce36d` |
| 3 | Identity Atlas | `Identity Atlas` | `identity-atlas` | 5002 | Node.js/Express/SQLite | `node server.js` | `d82569f` |
| 4 | Digital Sentinel | `Digital Sentinel` | `digital-sentinel` | 5002 | Node.js/Express/SQLite | `node server.js` | `33c6e91` |
| 5 | CK Writer | `CK-Writer` | `CK-writer` | 5004 | Node.js/Express/SQLite | `node server.js` | `383d97f` |
| 6 | Junk Drawer | `Junk Drawer file management system` | `junk-drawer` | 5005 | Python/Flask | `python app.py` | `ca336f1` |
| 7 | Opportunity Hunter | `Opportunity Hunter` | `opportunity-hunter` | 5006 | Python/Flask | `python app.py` | `cad6517` |
| 8 | Peterman | `Peterman` | `peterman` | 5008 | Node.js/Express/SQLite | `node server.js` | `120068d` |
| 9 | Costanza | `Costanza` | `costanza` | 5001 | Node.js/Express/SQLite | `node server.js` | `f8b76a3` |
| 10 | Learning Assistant | `Learning Assistant` | `learning-assistant` | 5012 | Node.js/Express/SQLite | `node server.js` | `fccbe36` |
| 11 | CK Learning Assistant | `ck-learning-assistant` | `ck-learning-assistant` | 5012 | Node.js/Express/SQLite | `node server.js` | `bd34083` |
| 12 | Swiss Army Knife | `Swiss Army Knife` | `ck-swiss-army-knife` | 5014 | Python/Flask | `python app.py` | `5869c8c` |
| 13 | AMTL TTS | `amtl-tts` | `amtl-tts` | 5015 | Python/FastAPI | `uvicorn src.app:create_app --port 5015` | `7448dd9` |
| 14 | Genie (AI Bookkeeper) | `Finance App/Genie` | `genie` | 8000 | Python/FastAPI/SQLite | `python -m uvicorn app:app --port 8000` | `11d22c5` |
| 15 | Accounting Genie | `Finance App/Accounting Genie` | `accounting-genie` | 8000 | Python/FastAPI/SQLite | `python -m uvicorn backend.app:app --port 8000` | `ab2c3ec` |
| 16 | AMTL Security | `amtl-security` | `amtl-security` | 8600 | Python/FastAPI | `uvicorn app:app --port 8600` | `09e5388` |
| 17 | Beast (Test Harness) | `beast` | `beast` | 8000 | Python/FastAPI | `uvicorn app.main:app --port 8000` | `4ebb9c9` |

## Libraries, Tools & Non-Server Repos

| # | Name | Folder | GitHub Repo | Purpose | Commit |
|---|------|--------|-------------|---------|--------|
| 1 | Proof | `proof` | `proof` | Test framework | `ebe0163` |
| 2 | Spark | `spark` | `spark` | Project scaffolding | `23ef784` |
| 3 | Beside You | `beside-you` | `beside-you` | AI companion | `48c8e14` |
| 4 | Dhamma Mirror | `dhamma-mirror` | `dhamma-mirror` | Meditation app | `0066054` |
| 5 | AI Safety Net | `ai-safety-net` | `ai-safety-net` | AI safety toolkit | `79536f9` |
| 6 | Audit Reports | `audit-reports` | `audit-reports` | Audit documentation | `a3d8bfa` |
| 7 | Signal v2 Semantic | `signal-v2-semantic` | `signal-v2-semantic` | Semantic search | `00dc954` |
| 8 | Signal Desktop | `signal-desktop` | `signal-desktop` | Desktop app | `2e92fda` |
| 9 | Elaine Desktop | `elaine-desktop` | `elaine-desktop` | Desktop app | `06ae077` |
| 10 | Your Project Hub | `your-project-hub` | `your-project-hub` | Project dashboard | `0bdb533` |
| 11 | Your Project Setup | `your-project-setup` | `your-project-setup` | Project setup wizard | `41fc839` |
| 12 | LLM Orchestrator | `LLM-Orchestrator-git` | `llm-router` | LLM routing | `89520db` |

## Archived Repositories

| # | Name | Folder | GitHub Repo | Commit | Archived Date |
|---|------|--------|-------------|--------|---------------|
| 1 | The Ledger | `The Ledger` | `the-ledger` | `b000bcb` | 2026-02-15 |
| 2 | Author Studio | `Author Studio-git` | `CK-Author-Studio` | N/A | 2026-02-15 |
| 3 | Signal (v1) | `signal-git` | `Signal` | `f641822` | 2026-02-15 |
| 4 | Elaine Mobile | `elaine-mobile` | `elaine-mobile` | N/A | 2026-02-15 |

## Port Registry Quick Reference

| Port | Application | Notes |
|------|-------------|-------|
| 5000 | Elaine | |
| 5001 | Ripple CRM | Costanza also defaults to 5001 |
| 5002 | Identity Atlas | Digital Sentinel also defaults to 5002 |
| 5004 | CK Writer | |
| 5005 | Junk Drawer | |
| 5006 | Opportunity Hunter | |
| 5008 | Peterman | |
| 5012 | Learning Assistant | CK Learning Asst also defaults to 5012 |
| 5014 | Swiss Army Knife | |
| 5015 | AMTL TTS | |
| 8000 | Genie | Accounting Genie & Beast also default to 8000 |
| 8600 | AMTL Security | |

## Non-Git Folders (Legacy/Manual)

| Folder | Contents |
|--------|----------|
| Elaine | Legacy Elaine (pre-v4), no git — preserved alongside Elaine-git |
| Author Studio | Manual files, no git |
| LLM-Orchestrator | Legacy files, no git — git clone at LLM-Orchestrator-git |
| signal | Legacy Signal files — git clone at signal-git |
| workshop | Local Flask app, no GitHub remote |
| ai-advisors | Manual files, no git |
| ck-desktop | Manual files, no git |
| desktop-apps | Manual files, no git |
| elaine-v3-phase1-2-3 | Archived Elaine v3 phases |

## PowerShell Start Commands

```powershell
$base = "C:\Users\ManiPadisetti\Dropbox\Desktop DB\Books and Articles Mani\Books\Almost Magic Tech Lab AMTL\Source and Brand\CK"

# Elaine (port 5000)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$base\Elaine-git'; python app.py"

# Ripple CRM (port 5001)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$base\Ripple CRM'; node server.js"

# Identity Atlas (port 5002)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$base\Identity Atlas'; node server.js"

# CK Writer (port 5004)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$base\CK-Writer'; node server.js"

# Junk Drawer (port 5005)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$base\Junk Drawer file management system'; python app.py"

# Opportunity Hunter (port 5006)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$base\Opportunity Hunter\backend'; python app.py"

# Peterman (port 5008)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$base\Peterman'; node server.js"

# Learning Assistant (port 5012)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$base\Learning Assistant'; node server.js"

# Swiss Army Knife (port 5014)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$base\Swiss Army Knife'; python app.py"

# AMTL TTS (port 5015)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$base\amtl-tts'; uvicorn src.app:create_app --port 5015"

# Genie (port 8000)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$base\Finance App\Genie'; python -m uvicorn app:app --port 8000"

# AMTL Security (port 8600)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$base\amtl-security'; uvicorn app:app --port 8600"
```

## Notes

- All repos synced from `github.com/Almost-Magic` organisation on 2026-02-15
- Port conflicts exist between some apps — run only one from each conflicting group at a time
- See `PORT_REGISTRY.md` in `audit-reports` repo for the authoritative port assignment plan
- See `start-all.ps1` for automated launcher script
- **CK-Writer** is on branch `node-rebuild` (default branch), not `main`
- **Hub** remote `ck-hub` no longer exists on GitHub — `your-project-hub` is the successor

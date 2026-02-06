# Elaine Desktop

**System tray app for Elaine — AI Chief of Staff**

Electron wrapper around Elaine's Flask API. Sits in your system tray, shows morning briefings, gravity field, gatekeeper status, and quick content checks.

## Prerequisites

- Node.js 18+
- Elaine v4 running on `http://127.0.0.1:5000`

## Setup

```bash
cd elaine-desktop
npm install
npm start
```

## Build Installer

```bash
npm run build-win    # Windows (.exe)
npm run build-mac    # macOS (.dmg)
```

## Features

- **System Tray**: Always accessible, click to show/hide
- **Morning Briefing**: Wellbeing state + compassion-aware opening
- **Gravity Field**: Top 5 priorities with force scores
- **Gatekeeper Status**: Items checked, held, overrides
- **Quick Check**: Paste content → instant Gatekeeper review

## Architecture

```
Elaine Desktop (Electron)
    ↓ HTTP
Elaine v4 (Flask, localhost:5000)
    ↓ modules
16 engines (Gravity, Sentinel, Compassion, Gatekeeper, etc.)
```

---

*Built by Almost Magic Tech Lab. Curated by Mani Padisetti.*

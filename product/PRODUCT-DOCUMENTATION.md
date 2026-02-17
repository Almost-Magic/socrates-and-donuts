# Socrates & Donuts - Product Documentation

## Overview

**Socrates & Donuts** is a self-reflection tool designed to help users gain clarity during emotional moments. It uses the Socratic method to guide users toward insight without giving advice.

## Core Philosophy

### The Mirror Metaphor
The app functions as a mirror—not a fix-it tool. Users don't come to be solved; they come to see themselves more clearly.

### Five Principles
1. **We don't fix — We help you see**
2. **We don't advise — Only questions, never answers**
3. **We don't replace people — Tool for clarity, then go to humans**
4. **We slow things down — Protect the pause**
5. **Seeing is enough — No gamification, no progress tracking**

## Features

### 1. The Mirror
AI-powered reflective conversation using Socratic questioning. Works in two modes:
- **Static Flows**: Pre-written question sequences for common situations (no API key needed)
- **AI Mode**: Claude or OpenAI-powered conversations (requires Bring Your Own Key)

### 2. The Vault
Lock reactive messages for 24 hours. Users write what they want to send, then lock it. After 24 hours, they can review with fresh eyes and decide whether to send, discard, or keep.

### 3. Letter You'll Never Send
A space to write unedited, uncensored letters. Includes a burning animation for symbolic release.

### 4. Emotional Weather Map
Track emotional patterns over time with visual representations of weather states (sunny, cloudy, stormy, etc.).

### 5. Body Compass
Map physical sensations to emotions. Users tap on a body diagram where they feel sensations and categorize them (pleasant/unpleasant/neutral).

### 6. Decision Journal
Log important decisions with reasoning and emotional state. Set review dates to revisit with fresh perspective.

### 7. Rewriter
Transform reactive or harsh language into neutral, clear communication—without changing meaning.

### 8. Wisdom Feed
Curated wisdom quotes from philosophers, spiritual teachers, and psychologists. Anti-doom scroll content.

### 9. Quick Capture
Fast thought capture with tags for later reflection.

## Technical Architecture

### Frontend
- **React 18** with TypeScript
- **Vite** for fast builds
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **Lucide React** for icons

### Data Storage
- **IndexedDB** for offline-first local storage
- No backend required—all data stays on device
- Export/Import functionality for backup

### AI Integration
- **Bring Your Own Key (BYOK)** model
- Supports **Claude** (Anthropic) and **OpenAI** GPT-4
- Static fallback flows work without API key

### Crisis Detection
- Priority safety feature
- Circuit breaker for self-harm language
- Directive response with resource surfacing

### PWA Support
- Installable as app
- Service worker for offline capability
- Manifest configuration

## Design System

### Colors
- **Background**: Midnight (#0A0E14)
- **Primary**: Gold (#C9944A)
- **Text**: Gray variants for hierarchy
- **Semantic**: Green (pleasant), Red (unpleasant/unlocked)

### Typography
- System font stack
- Clean, readable hierarchy
- 16px base size, comfortable line heights

## User Experience

### Onboarding
1. Welcome screen with core promise
2. Crisis resources clearly accessible
3. Optional API key setup for AI features
4. No account required

### Navigation
- Persistent sidebar or bottom nav on mobile
- Context-aware help on each screen
- Always-visible crisis button

### Data Privacy
- Local storage only
- No analytics
- No tracking
- Full data export/import

## Deployment

### GitHub Pages
Automatic deployment via GitHub Actions on main branch push.

### Build Output
- ~283KB JavaScript bundle (gzip: ~91KB)
- ~16KB CSS bundle (gzip: ~4KB)
- Total ~0.8KB HTML

## Contributing

### Development
```bash
npm install
npm run dev    # Development server at localhost:5173
npm run build  # Production build
npm run lint   # Code quality
```

### Architecture Principles
- Small, focused components
- Local-first data patterns
- Accessibility-first design
- No external dependencies for core flows

## License

MIT (code) · CC BY-NC (dictionary content)

---

*Sabbē sattā sukhī hontu — May all beings be happy.*

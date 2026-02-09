# BesideYou 🌿

**A companion for the cancer journey. Free, private, and always here.**

BesideYou is a free, open-source tool for cancer patients and their carers. It runs entirely in your browser — no server, no accounts, no tracking, no exceptions. We literally cannot see your data.

## What it does

- **Symptom Tracker** — Log how you're feeling, with severity and notes. Bring clearer notes to your doctor.
- **Medication Manager** — Keep all your medications, doses, and questions in one place.
- **Appointment Hub** — Questions for the doctor, pre-visit preparation, post-visit notes.
- **Good Days Jar** — Collect small moments of light. Revisit them on hard days.
- **Moments of Peace** — Breathing exercises and grounding techniques.
- **Private Journal** — A space for your thoughts. No one sees this but you.
- **Daily Check-in** — A few gentle questions about how things are going. Skip anything you like.
- **Carer Handoff** — Summarise the shift for the next carer. The hardest part of caregiving is the handoff.
- **Medical Glossary** — 40+ terms explained in plain language (expandable).
- **Australian Resources** — Crisis lines, support services, financial help. All free.
- **Crisis Support** — Emergency numbers, helplines, and breathing exercises. Always accessible.

## Privacy

Everything runs in your browser. There is no server. There is no database. There is no tracking.

Your data lives in your browser's local storage. You can export an encrypted backup (`.besideyou` file) and import it on another device. The encryption uses AES-256 with a passphrase you choose. Without your passphrase, no one can read it — including us.

If you clear your browser data, your data is gone — unless you saved a backup. That's the point.

## Running locally

```
git clone https://github.com/almost-magic/beside-you.git
cd beside-you
# Open index.html in your browser. That's it.
```

No build step. No npm install. No dependencies to manage. Just HTML, CSS, and JavaScript.

## Create a version for your community

BesideYou was built in Australia. Cancer doesn't respect borders, and neither should support.

### Fork for your country
1. Fork this repo
2. Edit `data.js` — change crisis numbers, resources, and helplines
3. Enable GitHub Pages in your repo settings
4. Your version is live

### Fork for a specific cancer type
1. Fork this repo
2. Edit `data.js` — add cancer-specific glossary terms, symptom suggestions, and resources
3. Adjust the welcome text and suggested prompts
4. Enable GitHub Pages

### Translate BesideYou
1. Fork this repo
2. Translate the text in `index.html` and `data.js`
3. **Tone matters.** This is not a technical document — it's a companion for people who are scared. Translate with care.

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidance.

## Architecture

```
index.html    — All screens and modals (single page application)
style.css     — All styling (dark/light theme, responsive)
data.js       — All content (glossary, resources, crisis numbers)
app.js        — All logic (state, rendering, export/import encryption)
```

No framework. No build tools. No server. Everything a contributor needs to understand is in four files.

## What this is not

- **Not medical advice.** BesideYou does not diagnose, treat, or recommend. Always talk to your care team.
- **Not a medical record.** This does not replace clinical documentation.
- **Not a social network.** Your data stays on your device.
- **Not a business.** There is no premium tier, no ads, no data collection. This is a gift.

## Safety

BesideYou should not be used in emergencies. If you or someone you care for is in danger, call **000** (Australia) or your local emergency number.

Crisis support is available 24/7:
- **Lifeline:** 13 11 14
- **Cancer Council:** 13 11 20
- **Beyond Blue:** 1300 22 4636

## Licence

MIT — do whatever you want with it. If it helps one person, it was worth building.

---

*A gift from [Almost Magic Tech Lab](https://almostmagic.au) · Sydney*

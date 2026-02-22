# AMTL — Peterman User Manual
## Document Code: AMTL-PTR-USR-1.0
## Almost Magic Tech Lab
## 18 February 2026

> *This document follows AMTL-ECO-STD v1.0. All conventions defined there apply unless explicitly overridden with a Decision Register entry.*

---

## Welcome

Peterman is your autonomous SEO and LLM presence engine. It monitors how AI sees your business, detects problems, generates solutions, and deploys fixes — while you get on with your day. Your role is to approve the big decisions. Peterman handles everything else.

---

## How to Access Peterman

| Method | How |
|--------|-----|
| **Ask ELAINE** | Say: "ELAINE, what's our Peterman Score?" or "ELAINE, show me the approval inbox" |
| **Workshop** | Click Peterman's card in The Workshop to launch the Electron app |
| **Browser** | Navigate to `localhost:5008` |
| **Mobile** | Approval notifications arrive via push (ntfy.sh). Open the approval link to approve/decline from your phone. |

---

## The War Room

The War Room is Peterman's main screen — a live intelligence centre for your domain's online presence.

### What You See

**Domain Cards (top):** Each managed domain shows a card with:
- Domain name
- Peterman Score (the circular gauge — higher is better)
- 30-day trend sparkline
- Active hallucinations count (red badge means there are problems to fix)
- Pending approvals count (amber badge means Peterman is waiting for your decision)
- Budget usage bar

**Chamber Map (centre):** A radial grid of all 11 intelligence chambers. Each tile pulses:
- **Green** = healthy, running normally
- **Amber** = attention needed, something detected
- **Red** = action pending, Peterman needs your approval

Click any chamber to see its detailed findings.

**Approval Inbox (bottom):** This is where you make decisions. Each card shows:
- What Peterman wants to do
- Why (one-line impact statement)
- Risk level (colour-coded badge)
- Expected Peterman Score impact
- **Approve**, **Decline**, or **Modify** buttons

**Active Alerts (right panel):** Real-time feed of issues sorted by severity.

---

## The Peterman Score

Your domain's health score on a 0–100 scale. It combines:
- How often AI mentions you (LLM Share of Voice)
- How close AI's understanding is to your ideal positioning (Semantic Gravity)
- Whether your website's technical infrastructure supports AI discovery (Technical Foundation)
- How well your content survives AI summarisation (Content Survivability)
- How many AI misconceptions exist about you (Hallucination Debt — lower is better)
- How you compare to competitors (Competitive Position)
- Whether you're positioned for future trends (Predictive Velocity)

**Score colours:**
- **Red (0–40):** Critical problems. Significant work needed.
- **Amber (40–65):** Some things working, but gaps exist.
- **Gold (65–85):** Healthy. Room for improvement, but you're in good shape.
- **Platinum (85–100):** Excellent. AI recommends you by default for your key queries.

Click the score gauge to expand the spider chart showing all component scores.

---

## Approving Actions

Peterman does most things automatically — but some actions need your sign-off.

### How Approvals Reach You

1. **Via ELAINE (voice):** ELAINE tells you what Peterman wants to do and asks for your OK.
   - Low-risk items: ELAINE announces them. If you don't object within 10 seconds, they proceed.
   - Medium-risk items: ELAINE asks and waits for your "yes" or "no."
   - High-risk items: ELAINE gives a detailed briefing and shows you a preview before you decide.

2. **Via the Approval Inbox (dashboard):** Open the War Room and review pending items at your own pace.

3. **Via mobile push:** Notifications arrive on your phone. Open the link to approve or decline.

### What the Risk Levels Mean

| Level | What It Means | Your Role |
|-------|---------------|-----------|
| Auto-deploy | Already done. Low risk, reversible. | Just review in the timeline if curious. |
| Low-gate | ELAINE announced it. | Object within 10 seconds if you disagree. |
| Medium-gate | Needs your yes/no. | Review the card and decide. |
| Hard-gate | High stakes. | Review the dry-run preview carefully before approving. |
| Prohibited | Peterman won't do this. | You do it manually. Peterman advises only. |

### Rolling Back a Decision

Changed your mind? Every deployed change can be undone:
1. Go to the **Journey Timeline**
2. Find the action you want to undo
3. Click **Rollback**
4. Confirm
5. Done — Peterman restores the previous version

Rollback is available for 30 days after deployment.

---

## Managing Domains

### Adding a New Domain

1. In the War Room, click **+ Add Domain**
2. Enter the domain URL (e.g., `almostmagic.net.au`)
3. Fill in: display name, CMS type, target LLMs, probe cadence, weekly budget
4. Click **Onboard**
5. Peterman runs an initial scan (takes 2–5 minutes):
   - Crawls the site
   - Detects CMS and technical setup
   - Runs first LLM probes
   - Generates initial Peterman Score
6. ELAINE briefs you on the results

### Viewing Domain Details

Click any Domain Card to enter that domain's War Room. From here you can:
- See all 11 chambers and their findings
- Review the approval inbox for that domain
- View the Journey Timeline (everything Peterman has done)
- Check the LLM Answer Diff View (how AI's answers changed over time)
- View the Semantic Neighbourhood Map (where you sit relative to competitors)

### Pausing a Domain

If you want Peterman to stop monitoring a domain temporarily:
1. Open the domain's settings
2. Change status to **Paused**
3. All probing and actions stop. Data is preserved.
4. Resume any time by changing status back to **Active**.

---

## Hallucinations

A "hallucination" is when AI says something incorrect about your business — like claiming you offer a service you don't, or confusing you with a competitor.

### Viewing Hallucinations

1. In the War Room, check the red badge on your Domain Card (shows active count)
2. Click to drill into the Hallucination Registry
3. Each hallucination shows:
   - What the AI said (the false claim)
   - Which AI said it (ChatGPT, Claude, Perplexity, etc.)
   - Severity (1–10)
   - Status: Open → Brief Generated → Content Deployed → Verified Closed

### How Peterman Fixes Them

Peterman's Hallucination Autopilot works like this:
1. Detects the false claim
2. Generates correction content (a new page, FAQ, or update)
3. Asks for your approval
4. Deploys the content
5. Waits 48 hours
6. Re-checks the AI to see if the hallucination is gone
7. If gone: marks it as "Verified Closed." If not: escalates with a stronger response.

You approve at step 3. Everything else is automatic.

---

## Content Briefs

Peterman generates content briefs — detailed instructions for what content should be written to improve your LLM presence. These briefs go to ELAINE, who writes the content using CK Writer.

### Reviewing a Brief

Each brief shows:
- Target query (the question this content should answer)
- Key facts that must be present
- Suggested headings
- Expected impact on your Peterman Score
- Alignment score (how well the written content matches the brief)

You approve the brief before ELAINE starts writing, and approve the finished content before deployment.

---

## The Journey Timeline

A chronological record of everything Peterman has done for a domain. Use this to:
- See what happened and when
- Verify that approved changes were deployed correctly
- Roll back any change within 30 days
- Generate evidence for client reporting

Each event shows: timestamp, which chamber triggered it, what was done, impact on Peterman Score, and a rollback button if applicable.

---

## Client Mode Reports

For client-facing reporting, Peterman generates a clean, branded PDF:
- Current Peterman Score with trend
- LLM Share of Voice per provider
- Top hallucinations fixed this period
- Content published and measured impact
- 90-day forward calendar preview

Generate on demand from the domain's War Room, or set up weekly auto-send.

---

## Dark/Light Mode

Toggle between dark and light mode using the button in the top-right header. Your preference is remembered across sessions. Default is dark (AMTL Midnight).

---

## Troubleshooting Quick Reference

| Problem | Quick Fix |
|---------|-----------|
| Peterman won't start | Check Workshop — is PostgreSQL running? Is port 5008 free? |
| Peterman Score shows "—" | Probes haven't completed yet. Wait for first cycle to finish. |
| Approval inbox is empty but ELAINE mentioned items | Refresh the War Room page. Check ELAINE integration health. |
| Hallucination marked "open" for weeks | Check if the correction content was approved and deployed. If deployed, re-probe may be pending. |
| "Partial data" badge on score | One or more LLM probe APIs were unavailable during the last cycle. Score will update on next successful cycle. |

For detailed troubleshooting, see **AMTL-PTR-DGN-1.0** (Diagnostic Playbook).

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `?` | Open context-aware help for current screen |
| `Esc` | Close help panel or modal |
| `a` | Jump to Approval Inbox |
| `t` | Jump to Journey Timeline |
| `r` | Refresh War Room data |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 18 February 2026 | Claude (Thalaiva) | Initial user manual — plain English, for Mani |

---

*Almost Magic Tech Lab*
*"You approve. Peterman executes. Your ranking improves."*
